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
  defaultList.value = '-';
  defaultList.text = '-';
  dropdownList.appendChild(defaultList);


  const saveButton = document.getElementById('saveButton');

  // Add event listener to the save button
  saveButton.addEventListener('click', saveData);


  // Step 1: First API call to populate dropdown1
  fetch('/getBoards', {
    mode: "cors"
  })
    .then(response => response.json())
    .then(data => {
      populateDropdown(dropdown, data);
      getLists()
    })
    .catch(error => console.error('Error fetching first API:', error));


  // Step 2: Event listener for dropdown1 changes
  dropdown.addEventListener('change', () => {
    getLists()
  });


  // Utility function to populate a dropdown
  function populateDropdown(dropdown, options) {
    dropdown.innerHTML = ''; // Clear existing options
    options.forEach(option => {
      const opt = document.createElement('option');
      opt.value = option.id; // Adjust based on your API response structure
      opt.textContent = option.name; // Adjust based on your API response structure
      dropdown.appendChild(opt);
    });
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
          populateDropdown(dropdownList, data);
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


});


t.render(function () {
  console.log(t.getContext());
  t.sizeTo('#content').done();
});
