from bidsbuilder.modules.file_bases.directories import Subject

hello = Subject()
print(hello)

hello2 = Subject()
print(hello2)

hello3 =Subject("TEST")
print(hello3)

print(hello._n_subjects)
print(hello._all_names)

hello4 = Subject("5")
print(hello4)

hello4.name = "TEST"