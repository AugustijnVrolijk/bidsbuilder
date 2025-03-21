from bids_conversion.util.queryASPEN import queryASPEN
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bids_conversion.deps.bids_dataset import BidsDataset

class DatasetDescription():
    def __init__(self, parent:"BidsDataset"):
        self.parent = parent
        self.root = parent.root
        pass

    def updateVals(self):
        pass


"""
    Create or update the dataset_description.json file for a fixed dataset.

    Parameters:
    - bids_root (str or Path): Path to the root of the BIDS dataset.

    Returns:
    - None
    
    # Path to the dataset_description.json file
    bids_root = Path(bids_root)

    # Check that the bids_root directory exists
    # if not bids_root.exists():
    #     raise FileNotFoundError(f"BIDS root directory does not exist: {bids_root}")

    description_file = bids_root / "dataset_description.json"

    # Hardcoded metadata
    description_data = {
        "Name": "iEEG Dataset 24H for Graz",
        "BIDSVersion": "1.6.0",
        "Authors": ["Hugo Sturkenboom, etc."],

    }

    # If the file already exists, merge with existing content
    if description_file.exists():
        print(f"Updating existing dataset_description.json: {description_file}")
        with open(description_file, "r") as f:
            existing_data = json.load(f)
        description_data = {**existing_data, **description_data}  # Merge existing and new data

    # Write to the dataset_description.json file
    with open(description_file, "w") as f:
        json.dump(description_data, f, indent=4)

    print(f"Dataset description saved at {description_file}")

"""

def main():
    pass

if __name__ == "__main__":
    main()