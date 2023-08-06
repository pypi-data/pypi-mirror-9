from rambutan3.type.matcher.seq.RRangeSizeSequenceMatcher import RRangeSizeSequenceMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum

NON_EMPTY_LIST = RRangeSizeSequenceMatcher(RSequenceEnum.LIST, min_size=1)
