from bidsbuilder.modules.data_folders import DatasetSubject

hello = DatasetSubject()
print(hello)

hello2 = DatasetSubject()
print(hello2)

hello3 =DatasetSubject("TEST")
print(hello3)

print(hello._n_subjects)
print(hello._all_names)

hello4 = DatasetSubject("5")
print(hello4)

hello4.name = "TEST"