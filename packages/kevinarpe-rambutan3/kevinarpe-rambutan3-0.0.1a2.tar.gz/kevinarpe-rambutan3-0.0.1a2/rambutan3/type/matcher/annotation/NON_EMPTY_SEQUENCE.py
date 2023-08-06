from rambutan3.type.matcher.seq.RRangeSizeSequenceMatcher import RRangeSizeSequenceMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum

NON_EMPTY_SEQUENCE = RRangeSizeSequenceMatcher(RSequenceEnum.SEQUENCE, min_size=1)
