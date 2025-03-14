// Loads up the Trello iframe and applies the styling
const t = window.TrelloPowerUp.iframe();
console.log("IFRAME")
document.addEventListener("DOMContentLoaded", function () {


  const dropdown = document.getElementById('boardDropdown');
  // Preselected default text
  const defaultBoard = document.createElement('option');
  defaultBoard.value = "Select";
  defaultBoard.text = "Select the board";
  dropdown.appendChild(defaultBoard);


  const dropdownList = document.getElementById('listDropdown');
  // Preselected default text
  const defaultList = document.createElement('option');
  defaultList.value = '';
  defaultList.text = 'Select the list';
  dropdownList.appendChild(defaultList);
  dropdownList.disabled = true;


  const saveButton = document.getElementById('saveButton');
  saveButton.disabled = true;

  const removeButton = document.getElementById('removeButton');


  // Add event listener to the save button
  saveButton.addEventListener('click', saveData);

  // Add event listener to the remove button
  removeButton.addEventListener('click', removeCard);





  // Step 1: First API call to populate dropdown1
  fetch('/getBoards', {
    mode: "cors"
  })
    .then(response => response.json())
    .then(data => {
      populateBoardDropdown(dropdown, data);
      getLists()
    })
    .catch(error => console.error('Error fetching first API:', error));


  // Step 2: Event listener for dropdown1 changes
  dropdown.addEventListener('change', () => {
    getLists()
  });


  // Utility function to populate a dropdown
  function populateBoardDropdown(dropdown, options) {
    dropdown.innerHTML = ''; // Clear existing options

    // Create and append the default option
    const defaultOption = document.createElement('option');
    defaultOption.value = ''; // Empty value (so it's not selectable)
    defaultOption.textContent = 'Select the board';
    defaultOption.disabled = true; // Make it non-selectable
    defaultOption.selected = true; // Set as default
    dropdown.appendChild(defaultOption);

    options.forEach(option => {
      const opt = document.createElement('option');
      opt.value = option.id; // Adjust based on your API response structure
      opt.textContent = option.name; // Adjust based on your API response structure
      dropdown.appendChild(opt);
    });

    // Remove the default option when the user clicks the dropdown
    dropdown.addEventListener('focus', function () {
      if (dropdown.options[0].disabled) {
        dropdown.remove(0); // Remove first option
      }
    }, { once: true }); // Ensures it only runs the first time
  }

  // Utility function to populate a dropdown
  function populateListDropdown(dropdown, options) {
    dropdown.innerHTML = ''; // Clear existing options
    dropdown.disabled = false;

    options.forEach(option => {
      const opt = document.createElement('option');
      opt.value = option.id; // Adjust based on your API response structure
      opt.textContent = option.name; // Adjust based on your API response structure
      dropdown.appendChild(opt);
    });

    saveButton.disabled = false;
  }


  async function getLists() {
    const selectedValue = dropdown.value;

    // Clear dropdown2 while loading new options
    //clearDropdown(dropdownList);

    // Step 3: Second API call to populate dropdown2 based on dropdown1 value
    if (selectedValue) {
      await fetch(`/getFilteredListsOnBoard?boardID=${selectedValue}`, {
        mode: "cors"
      })
        .then(response => response.json())
        .then(data => {
          populateListDropdown(dropdownList, data);
        })
        .catch(error => console.error('Error fetching second API:', error));
    }
  }


  // Function to handle the save button click
  async function saveData() {
    const selectedBoard = dropdown.value;
    const selectedList = dropdownList.value;

    if (!selectedBoard || !selectedList) {
      alert('Please select both a board and a list before saving.');
      return;
    }

    // console.log(t.card())
    const tempid = t.getContext().card
    console.log(`This is current card id: ${tempid}`)

    const payload = {
      listID: selectedList,
      originalCardID: tempid
    };


    try {
      const response = await fetch('/createMirrorCard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
        mode: "cors"
      });

      if (response.ok) {
        alert('Selection saved successfully!');
      } else {
        console.error('Error saving data:', response.statusText);
        alert('Failed to save selection. Please try again.');
      }
    } catch (error) {
      console.error('Error during save request:', error);
      alert('An error occurred while saving. Please try again.');
    }
  }


  // Function to handle remove button
  async function removeCard() {
    cardID = '67d4901647e1310e45ba71f1';
   

    // Step 1: First API call to populate dropdown1
  fetch(`/getMirroredCards?cardID=${cardID}`, {
    mode: "cors"
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("Error fetching data:", error));

  }

});


t.render(function () {
  console.log(t.getContext());
  t.sizeTo('#content').done();
});
