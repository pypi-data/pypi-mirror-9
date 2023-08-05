"""
Deuce Valere - Client - Valere
"""
import datetime
import logging

from deuceclient.api import Block
from deuceclient.common import errors as deuce_errors
from stoplight import validate

from deucevalere.common.validation import *
from deucevalere.common.validation_instance import *


class ValereClient(object):

    @validate(deuce_client=ClientRule,
              vault=VaultInstanceRule,
              manager=ValereManagerRule)
    def __init__(self, deuce_client, vault, manager):
        self.deuceclient = deuce_client
        self.vault = vault
        self.manager = manager
        self.log = logging.getLogger(__name__)

    def get_block_list(self):
        """Fill the Manager's list of current blocks
        """
        self.manager.metadata.current = []

        marker = self.manager.start_block

        self.log.info('Project ID: {0}, Vault {1} - '
                 'Searching for Blocks [{2}, {3})'
                 .format(self.vault.project_id,
                         self.vault.vault_id,
                         marker,
                         self.manager.end_block))

        while True:
            for block_id in self.deuceclient.GetBlockList(self.vault,
                                                          marker=marker):
                if self.manager.end_block is not None:
                    if block_id < self.manager.end_block:
                        self.manager.metadata.current.append(block_id)
                    else:
                        break
                else:
                    self.manager.metadata.current.append(block_id)

            marker = self.vault.blocks.marker
            self.log.debug('Next Marker: {0}'.format(marker))

            if marker is None:
                break

    @staticmethod
    @validate(metadata_id=MetadataBlockIdRuleNoneOkay)
    def _convert_metadata_id_to_storage_id(metadata_id):
        """Return a 'valid' storage id that is the lowest possible value

        Note: This will need to be updated when the format of the
              storage id changes.

        Note: It is impossible to create a UUID that is guarateed to be the
              lowest possible value using a UUID generator. However, UUIDs
              are alphanumeric values; thus '0' is always the lowest value
              and filling out a formatstring that looks like a UUID string
              but uses all zeros (0) will giveus a string that will compare
              as the lowest possible UUID value.
        """
        if metadata_id is not None:
            return '{0:}_{1:}-{2:}-{2:}-{2:}-{3:}'.format(metadata_id,
                                                          '{:08X}'.format(0),
                                                          '{:04X}'.format(0),
                                                          '{:012X}'.format(0))
        else:
            return None

    def get_storage_list(self):
        """Fill the manager's list of current storage blocks
        """
        self.manager.storage.current = []

        start_marker = ValereClient._convert_metadata_id_to_storage_id(
            self.manager.start_block)
        end_marker = ValereClient._convert_metadata_id_to_storage_id(
            self.manager.end_block) if self.manager.end_block else None

        self.log.info('Project ID: {0}, Vault {1} - '
                 'Searching for Storage Blocks [{2}, {3})'
                 .format(self.vault.project_id,
                         self.vault.vault_id,
                         start_marker,
                         end_marker))

        while True:
            for block_id in self.deuceclient.GetBlockStorageList(
                    self.vault, marker=start_marker):

                if end_marker is not None:
                    if block_id < end_marker:
                        self.manager.storage.current.append(block_id)
                    else:
                        break
                else:
                    self.manager.storage.current.append(block_id)

            start_marker = self.vault.storageblocks.marker
            self.log.debug('Next Marker: {0}'.format(start_marker))

            if start_marker is None:
                break

    def validate_metadata(self):
        """Validate a block

        Access each block through a HEAD operation
        Checks if the reference count is zero
        For blocks with zero reference counts mark them as expired if they
        pass the age specified by the manager
        """
        # Note: THis function is a little more verbose since it is detecting
        #       which blocks to delete.
        if self.manager.metadata.current is None:
            self.get_block_list()

        if len(self.manager.metadata.current) == 0:
            self.get_block_list()

        if self.manager.metadata.expired is None:
            self.manager.metadata.expired = []

        # Loop over any known blocks and validate them
        for block_id in self.manager.metadata.current:
            self.log.debug('Project ID {0}, Vault {1} - '
                           'Validating Block: {2}'
                           .format(self.vault.project_id,
                                   self.vault.vault_id,
                                   block_id))

            try:
                # Access the block so that Deuce validates it all internally
                block = self.deuceclient.HeadBlock(self.vault,
                                                   self.vault.blocks[block_id])

            except deuce_errors.MissingBlockError as missing_ex:
                self.log.warn('Project ID {0}, Vault {1} - '
                              'Block {2} error missing storage block '
                              .format(self.vault.project_id,
                                      self.vault.vault_id,
                                      block_id))
                self.manager.missing_counter.add(1, 0)
                block = None

            except Exception as ex:
                # if there was a problem just mark the block as None so it
                # get ignored for this iteration of the loop
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Block {2} error heading block ({3}): {4}'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 block_id,
                                 type(ex),
                                 str(ex)))
                block = None

            # if there was a problem then go to the next block_id
            if block is None:
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Block {2} no block data to analyze'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 block_id))
                continue

            # Now check if the block has any references
            if int(block.ref_count) == 0:
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Block {2} has no references'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 block_id))
                # Try to calculate the age of the block since it was
                # last modified

                block_age = datetime.datetime.utcnow() - \
                    datetime.datetime.utcfromtimestamp(block.ref_modified)
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Block {2} has age {3}'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 block_id,
                                 block_age))

                # If the block age is beyond the threshold then mark it
                # for deletion
                if block_age > self.manager.expire_age:
                    self.log.info('Project ID {0}, Vault {1} - '
                             'Found Expired Block: {2}'
                             .format(self.vault.project_id,
                                     self.vault.vault_id,
                                     block_id))

                    # If we have already marked it for deletion then
                    # do not add it a second time; try to keep the list
                    # to a minimum
                    if block_id not in self.manager.metadata.expired:
                        self.manager.expired_counter.add(1, len(block))
                        self.manager.metadata.expired.append(block_id)

            else:
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Block {2} has {3} references'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 block_id,
                                 block.ref_count))

        for block_id in self.manager.metadata.expired:
            # there _should_ only be one instance of a block_id in the
            # current list; but loop over it just in case since remove()
            # only removes the first instance it finds
            while block_id in self.manager.metadata.current:
                self.manager.metadata.current.remove(block_id)

    def cleanup_expired_blocks(self):
        """Delete expired blocks

        Attempt to delete each expired block
        On success, adds the block to a list of deleted blocks and removes
        the block id from the list of expired blocks

        Note: A block deletion may fail for numerous reasons including that
              the block received a change in its reference count to being
              non-zero between when it was detected as being expired and
              when the deletion operation occurred. This is a designed
              feature of Deuce so that blocks are not accidentally or
              improperly removed.
        """
        # Note: This function must be very verbose in its logging since it
        #       it removing user data that will not be recoverable from
        #       within Deuce

        # Check if there is a list to operate on; if not throw an error
        if self.manager.metadata.expired is not None:

            # Keep track of any block we successfully deleted
            if self.manager.metadata.deleted is None:
                self.manager.metadata.deleted = []

            # Attempt to delete all expired blocks
            for expired_block_id in self.manager.metadata.expired:

                # Check to see if we have already deleted the block
                if expired_block_id not in self.manager.metadata.deleted:

                    # Log that we are going to delete the block
                    self.log.info('Project ID {0}, Vault {1} - '
                                  'Deleting Expired Block: {2}'
                                  .format(self.vault.project_id,
                                          self.vault.vault_id,
                                          expired_block_id))

                    # Attempt to delete the block
                    # Note: This may fail for numerous reasons, including
                    #       that the block received a reference count between
                    #       when it was deteremined not to have any and when
                    #       the cleanup tried to remove it.
                    try:
                        self.deuceclient.DeleteBlock(self.vault,
                                                     self.vault.blocks[
                                                         expired_block_id])

                        # The block was deleted, save it as being so
                        # This serves two purposes:
                        #   1. Do not attempt to delete the same block twice
                        #   2. Do not mutate the expired block list while it
                        #      is being traversed; it'll get cleaned up later
                        self.manager.metadata.deleted.append(expired_block_id)

                        block_size = len(self.vault.blocks[
                            expired_block_id])
                        self.manager.delete_expired_counter.add(1,
                                                         block_size)
                        self.log.info('Project ID {0}, Vault {1} - '
                                      'Successfully Deleted Expired Block: {2}'
                                      .format(self.vault.project_id,
                                              self.vault.vault_id,
                                              expired_block_id))
                    except Exception as ex:
                        self.log.info('Project ID {0}, Vault {1} - '
                                      'FAILED to Deleted Expired Block '
                                      '({2}): {3}'
                                      .format(self.vault.project_id,
                                              self.vault.vault_id,
                                              expired_block_id,
                                              str(ex)))
                else:
                    self.log.info('Project ID {0}, Vault {1} - '
                                  'Already Deleted Expired Block: {2}'
                                  .format(self.vault.project_id,
                                          self.vault.vault_id,
                                          expired_block_id))

            # Now cleanup the expired list to remove the blocks that were
            # Actually deleted
            for deleted_block_id in self.manager.metadata.deleted:
                while deleted_block_id in self.manager.metadata.expired:
                    self.manager.metadata.expired.remove(deleted_block_id)
        else:
            raise RuntimeError('No expired blocks to remove.'
                               'Please run validate_metadata() first.')

    def build_cross_references(self, skip_expired=False):
        """Build a cross reference look-up for the metadata and storage ids

        Primary purpose is to have a quick way to do a reverse lookup of
        storage ids to determine validity based on the information we
        already have.

        :param skip_expired: boolean value for whether or not to include the
                             expired metadata blocks in the cross reference
                             data. Default is False which removes them from
                             the cross reference data.
        """

        check_expired = self.manager.metadata.expired is not None
        check_deleted = self.manager.metadata.deleted is not None

        if skip_expired:
            check_expired = False

        for block_id, block in self.vault.blocks.items():
            storage_id = block.storage_id
            self.log.debug('Project ID {0}, Vault {1} - '
                           'Checking status of Storage ID {2} '
                           'with Block ID {3}'
                           .format(self.vault.project_id,
                                   self.vault.vault_id,
                                   storage_id,
                                   block_id))

            # Skip the block if it was expired
            if check_expired:
                if block_id in self.manager.metadata.expired:
                    self.log.debug('Project ID {0}, Vault {1} - '
                                   'block {2} expired, not '
                                   'cross-referencing'
                                   .format(self.vault.project_id,
                                           self.vault.vault_id,
                                           block_id))
                    continue

            # Skip the block if it was deleted
            if check_deleted:
                if block_id in self.manager.metadata.deleted:
                    self.log.debug('Project ID {0}, Vault {1} - '
                                   'block {2} deleted, not '
                                   'cross-referencing'
                                   .format(self.vault.project_id,
                                           self.vault.vault_id,
                                           block_id))
                    continue

            # lookup the storage id
            self.log.debug('Project ID {0}, Vault {1} - '
                           'Mapping Storage ID {2} to Block ID {3}'
                           .format(self.vault.project_id,
                                   self.vault.vault_id,
                                   storage_id,
                                   block_id))

            # Add it to the cross-reference dict
            self.manager.cross_reference[storage_id] = block_id

    def validate_storage(self, skip_expired=False):
        """Check storage for orphaned blocks

        This implements the short version where we only operate on the
        listing of the storage blocks.

        :param skip_expired: Parameter to call to build_cross_references().
                             See build_cross_references() for details.

        Note: In some cases it may be advantageous to include the expired
              metadata blocks in the cross-reference data in order to keep
              their associated storage blocks from incorrectly being
              detected as orphaned blocks. This is primarily due to an
              order of operations issue when validating both metadata and
              storage prior to performing the actual block deletions. In
              these instances, set skip_expired to True to avoid improper
              detection of orphaned blocks that are not really orphaned.
        """

        if self.manager.storage.current is None:
            self.get_storage_list()

        if len(self.manager.storage.current) == 0:
            self.get_storage_list()

        if self.manager.storage.orphaned is None:
            self.manager.storage.orphaned = []

        # This builds a quick lookup which provides the following benefits:
        #   1. We do not have to look at self.vault.blocks every time
        #   2. We do not need to rely on the format of the storage block id to
        #      determine the metadata block id
        self.build_cross_references(skip_expired)

        if len(self.manager.cross_reference) == 0:
            self.log.warn('Project ID {0}, Vault {1} - no cross-references '
                          'between metadata and storage. All blocks will be'
                          'marked as orphaned for metadata block range '
                          '[{2}, {3})'
                          .format(
                              self.vault.project_id,
                              self.vault.vault_id,
                              self.manager.start_block,
                              self.manager.end_block))

        # Note: Marking a block orphaned here does not necessarily mean it is
        #       actually orphaned as there could have been activity on the
        #       Vault since we got the listings that could change the state of
        #       any block.This cuts both ways in that some blocks we determine
        #       are orphaned may not be orphaned, while other blocks we think
        #       are not orphaned are actually orphaned. This is okay as Deuce
        #       is designed to prevent deletion of non-ophaned blocks, and
        #       blocks that are not identified as orphaned but really are will
        #       be picked up on the next run.
        for storage_id in self.manager.storage.current:
            if storage_id not in self.manager.cross_reference:
                self.log.info('Project ID {0}, Vault {1} - '
                              'Found Orphaned Storage Block {2}'
                              .format(
                                  self.vault.project_id,
                                  self.vault.vault_id,
                                  storage_id))
                self.manager.storage.orphaned.append(storage_id)

                block_size = len(self.vault.storageblocks[storage_id])

                if block_size == 0:
                    mid, sid = storage_id.split('_')

                    if mid in self.vault.blocks:
                        self.log.info('Project ID {0}, Vault {1} - '
                                      'Located block {2} matching '
                                      'orphaned block {3}. Using for '
                                      'block size'.format(
                                          self.vault.project_id,
                                          self.vault.vault_id,
                                          mid,
                                          storage_id))
                        block_size = len(self.vault.blocks[mid])
                self.manager.orphaned_counter.add(1, block_size)

    def validate_storage_with_head(self):
        """Check storage for orphaned blocks

        This implements the long version where we operate on the listing
        of the storage blocks and also HEAD each block in storage
        """
        if self.manager.storage.current is None:
            self.get_storage_list()

        if len(self.manager.storage.current) == 0:
            self.get_storage_list()

        if self.manager.storage.orphaned is None:
            self.manager.storage.orphaned = []

        # Note: This version relies on Deuce to tell us that a block is
        #       orphaned so it is the most accurate at the time this
        #       function is called. However, there is still the chance that
        #       a block has a change of state between when we access it here
        #       and when it actually gets cleaned up
        for storage_id in self.manager.storage.current:

            self.log.debug('Project ID {0}, Vault {1} - '
                           'Validating Storage Block: {2}'
                           .format(self.vault.project_id,
                                   self.vault.vault_id,
                                   storage_id))
            try:
                block = self.deuceclient.HeadBlockStorage(self.vault,
                                                          self.vault.
                                                          storageblocks[
                                                              storage_id])
            except Exception as ex:
                # if there was a problem just mark the block as None so it
                # get ignored for this iteration of the loop
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Storage Block {2} error heading block ({3}): {4}'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 storage_id,
                                 type(ex),
                                 str(ex)))
                block = None

            # if there was a problem then go to the next block_id
            if block is None:
                self.log.warn('Project ID {0}, Vault {1} - '
                         'Storage Block {2} no block data to analyze'
                         .format(self.vault.project_id,
                                 self.vault.vault_id,
                                 storage_id))
                continue

            if block.block_orphaned:
                self.log.info('Project ID {0}, Vault {1} - '
                              'Found Orphaned Storage Block {2}'
                              .format(
                                  self.vault.project_id,
                                  self.vault.vault_id,
                                  storage_id))
                self.manager.storage.orphaned.append(storage_id)

                block_size = len(block)

                self.log.info('Storage Block ID {0} - block size {1}'
                              .format(storage_id, block_size))

                if block_size == 0:
                    mid, sid = storage_id.split('_')

                    self.log.info('\tBlock ID: {0}'.format(mid))
                    self.log.info('\tStorage UUID: {0}'.format(sid))

                    if mid in self.vault.blocks:
                        self.log.info('\tBlock ID {0} in Vault'.format(mid))

                        self.log.info('Project ID {0}, Vault {1} - '
                                      'Located block {2} matching '
                                      'orphaned block {3}. Using for '
                                      'block size'.format(
                                          self.vault.project_id,
                                          self.vault.vault_id,
                                          mid,
                                          storage_id))
                        self.log.info('\tUpdating Block Size from {0} to {1}'
                                      .format(block_size,
                                              len(self.vault.blocks[mid])))
                        block_size = len(self.vault.blocks[mid])
                self.manager.orphaned_counter.add(1, block_size)

    def calculate_current(self):
        """Calculate the amount of data that is still current
        """

        if self.manager.metadata.current is not None:
            for block_id in self.manager.metadata.current:
                block_size = len(self.vault.blocks[block_id])
                self.manager.current_counter.add(1, block_size)

    def cleanup_storage(self):
        """Delete orphaned blocks from storage

        Attempt to delete each orphaned block
        On success, adds the block to the list deleted blocks and removes
        the storage id from the orphaned blocks

        Note: A block deletion may fail for numerous reasons including that
              the block received a change in its state so it is no longer
              orphaned between when it was detected as orphaned and when
              the deletion operation occurred. This is a designed feature
              of Deuce so that blocks that blocks are not accidentally or
              improperly removed.
        """
        # Note: This function must be very verbose in its logging since it
        #       it removing user data that will not be recoverable from
        #       within Deuce

        # Check if there is a list to operate on; if not throw an error
        if self.manager.storage.orphaned is not None:

            # Keep track of any block we successfully deleted
            if self.manager.storage.deleted is None:
                self.manager.storage.deleted = []

            # Attempt to delete all expired blocks
            for orphaned_storage_block_id in self.manager.storage.orphaned:

                # Check to see if we have already deleted the block
                if orphaned_storage_block_id not in \
                        self.manager.storage.deleted:

                    # Log that we are going to delete the block
                    self.log.info('Project ID {0}, Vault {1} - '
                                  'Deleting Orphaned Block: {2}'
                                  .format(self.vault.project_id,
                                          self.vault.vault_id,
                                          orphaned_storage_block_id))

                    # Attempt to delete the block
                    # Note: This may fail for numerous reasons, including
                    #       that the block received a reference count between
                    #       when it was deteremined not to have any and when
                    #       the cleanup tried to remove it.
                    try:
                        osbid = orphaned_storage_block_id
                        orphaned_block = Block(self.vault.project_id,
                                               self.vault.vault_id,
                                               block_id=None,
                                               storage_id=osbid,
                                               block_type='storage')
                        self.deuceclient.DeleteBlockStorage(self.vault,
                                                            orphaned_block)

                        # The block was deleted, save it as being so
                        # This serves two purposes:
                        #   1. Do not attempt to delete the same block twice
                        #   2. Do not mutate the orphaned block list while it
                        #      is being traversed; it'll get cleaned up later
                        self.manager.storage.deleted.append(
                            orphaned_storage_block_id)

                        # By default this will be zero and this should be
                        # valid since the oprhaned_storage_block_id comes
                        # from listing the storage blocks to start with
                        block_size = len(self.vault.storageblocks[
                            orphaned_storage_block_id])

                        if block_size == 0:
                            mid, sid = orphaned_storage_block_id.split('_')

                            if mid in self.vault.blocks:
                                self.log.info('Project ID {0}, Vault {1} - '
                                              'Located block {2} matching '
                                              'orphaned block {3}. Using for '
                                              'block size'.format(
                                                  self.vault.project_id,
                                                  self.vault.vault_id,
                                                  mid,
                                                  orphaned_storage_block_id))
                                block_size = len(self.vault.blocks[mid])

                        self.manager.delete_orphaned_counter.add(1, block_size)

                        self.log.info('Project ID {0}, Vault {1} - '
                                      'Successfully Deleted Orphaned Block: '
                                      '{2}'
                                      .format(self.vault.project_id,
                                              self.vault.vault_id,
                                              orphaned_storage_block_id))
                    except Exception as ex:
                        self.log.info('Project ID {0}, Vault {1} - '
                                      'FAILED to Deleted Orphaned Block '
                                      '({2}): {3}'
                                      .format(self.vault.project_id,
                                              self.vault.vault_id,
                                              orphaned_storage_block_id,
                                              str(ex)))
                else:
                    self.log.info('Project ID {0}, Vault {1} - '
                                  'Already Deleted Orphaned Block: {2}'
                                  .format(self.vault.project_id,
                                          self.vault.vault_id,
                                          orphaned_storage_block_id))

            # Now cleanup the orphaned list to remove the blocks that were
            # Actually deleted
            for deleted_block_id in self.manager.storage.deleted:
                while deleted_block_id in self.manager.storage.orphaned:
                    self.manager.storage.orphaned.remove(deleted_block_id)
        else:
            raise RuntimeError('No orphaned blocks to remove.'
                               'Please run validate_storage() '
                               'or validate_storage_with_head() first.')
