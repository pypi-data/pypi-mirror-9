import uuid
import calendar
import mmh3


_number_types = frozenset((int, long, float))


def make_foreign_id_uuid(time_arg, data):
    '''
    Returns UUID version 1 with constant values for given time data
    UUID randomization is ignored and replaced by the digest of data

    '''

    if isinstance(time_arg, uuid.UUID):
        return time_arg

    if hasattr(time_arg, 'utctimetuple'):
        seconds = int(calendar.timegm(time_arg.utctimetuple()))
        microseconds = (seconds * 1e6) + time_arg.time().microsecond
    elif type(time_arg) in _number_types:
        microseconds = int(time_arg * 1e6)
    else:
        raise ValueError('Argument for a v1 UUID column name or value was ' +
                         'neither a UUID, a datetime, or a number')

    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = int(microseconds * 10) + 0x01b21dd213814000L

    time_low = timestamp & 0xffffffffL
    time_mid = (timestamp >> 32L) & 0xffffL
    time_hi_version = (timestamp >> 48L) & 0x0fffL

    # For the clock_seq_hi_variant, we don't get to pick the two most
    # significant bits (they're always 10), so we are dealing with a
    # positive byte range for this particular byte.

    # Make the lowest value UUID with the same timestamp
    clock_seq_low = 0x80L
    clock_seq_hi_variant = 0 & 0x80L  # The two most significant bits
    # will be 10 for the variant

    # 32 bits signed int murmur digest
    digested_data = mmh3.hash(data)

    # make sure we keep the bit sign
    if digested_data > 0:
        sign_mask = 0x100000000L
    else:
        sign_mask = 0x000000000L

    # make sure we keep the sign information
    node = abs(digested_data) | sign_mask

    # make sure node is 48 bits
    node = node | 0x800000000000L

    return uuid.UUID(fields=(time_low, time_mid, time_hi_version,
                             clock_seq_hi_variant, clock_seq_low, node), version=1)
