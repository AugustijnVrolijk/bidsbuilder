

from bidsbuilder import BidsDataset

test = BidsDataset()
print("hello")

sub1 = test.add_subject(1)

sub1.datatype = "FMRI"