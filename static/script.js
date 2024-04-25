document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM Content loaded");
  const slotSelect = document.getElementById("slot-select");
  const statsSelect = document.getElementById("stats-select");

  let currentSlot = null;
  let currentStats = null;

  // Initial population and URL parameter handling
  function initializeFromURL() {
    console.log("initializeFromURL loaded");
    const urlParams = new URLSearchParams(window.location.search);
    const slotParam = urlParams.get("slot");
    const statsParam = urlParams.get("stats");

    if (slotParam) {
      currentSlot = slotParam;
      slotSelect.value = slotParam;
      fetch(`/get_stats_for_slot/${slotParam}`)
        .then((response) => response.json())
        .then((stats) => populateDropdown(statsSelect, stats));
    }

    if (statsParam) {
      currentStats = statsParam;
      statsSelect.value = statsParam;
    }

    loadInitialTable(); // Load the initial table
  }

  function loadInitialTable() {
    // Logic from the beginning of your refreshTable function:
    const selectedSlot = slotSelect.value; // Get initial slot if available (or leave empty)
    const selectedStats = statsSelect.value; // Get initial stats if available (or leave empty)

    let url = "/get_table_data";

    const params = new URLSearchParams();
    if (selectedSlot) {
      params.append("slot", selectedSlot);
    }
    if (selectedStats) {
      params.append("stats", selectedStats);
    }
    url += params.toString() ? "?" + params.toString() : "";

    fetch(url) // Fetch with parameters included
      .then((response) => response.text())
      .then((newTableHTML) => {
        // console.log("Received Table HTML:", newTableHTML);
        const tableContainer = document.getElementById("table-container");
        tableContainer.innerHTML = newTableHTML;
      })
      .catch((error) => {
        console.error("Error fetching table data:", error);
      });
  }

  // Dropdown population helper function
  function populateDropdown(dropdown, options) {
    dropdown.innerHTML = "";

    let option = document.createElement("option");
    option.value = "";
    option.text = "All";
    dropdown.appendChild(option);

    options.forEach((optionValue) => {
      let option = document.createElement("option");
      option.value = optionValue;
      option.text = optionValue;
      dropdown.appendChild(option);
    });
  }

  // Function to populate dropdowns
  function populateDropdowns(slotSelect, statsSelect) {
    fetch("/get_slots")
      .then((response) => response.json())
      .then((slots) => populateDropdown(slotSelect, slots));

    slotSelect.addEventListener("change", () => {
      const selectedSlot = slotSelect.value;
      statsSelect.innerHTML = "";

      if (selectedSlot) {
        fetch(`/get_stats_for_slot/${selectedSlot}`)
          .then((response) => response.json())
          .then((stats) => populateDropdown(statsSelect, stats));
      }
    });
  }

  populateDropdowns(slotSelect, statsSelect);

  slotSelect.addEventListener("change", (event) => {
    event.preventDefault();
    const selectedSlot = slotSelect.value;

    if (selectedSlot !== currentSlot) {
      currentSlot = selectedSlot;

      const statsSelect = document.getElementById("stats-select");
      const statsPlaceholder = document.getElementById("stats-placeholder");

      // Logic for hiding empty second dropdown
      if (selectedSlot === "") {
        statsPlaceholder.classList.remove("hide");
        statsPlaceholder.classList.add("show");
        statsSelect.classList.remove("show");
        statsSelect.classList.add("hide");
      } else {
        statsPlaceholder.classList.remove("show");
        statsPlaceholder.classList.add("hide");
        statsSelect.classList.remove("hide");
        statsSelect.classList.add("show");

        // Fetch stats corresponding to a specific slot
        fetch(`/get_stats_for_slot/${selectedSlot}`)
          .then((response) => response.json())
          .then((stats) => populateDropdown(statsSelect, stats));
      }

      refreshTable();
    }
  });

  // Refresh the able upon selections in dropdowns
  function refreshTable() {
    const selectedSlot = slotSelect.value;
    const selectedStats = statsSelect.value;

    let url = "/get_table_data"; // Base URL

    // Construct query parameters
    const params = new URLSearchParams();
    if (selectedSlot) {
      params.append("slot", selectedSlot);
    }
    if (selectedStats) {
      params.append("stats", selectedStats);
    }
    url += params.toString() ? "?" + params.toString() : ""; // Conditional appending

    fetch(url)
      .then((response) => response.text())
      .then((newTableHTML) => {
        const tableContainer = document.getElementById("table-container");
        tableContainer.innerHTML = newTableHTML;
      })
      .catch((error) => {
        console.error("Error fetching table data:", error);
      });
  }

  statsSelect.addEventListener("change", (event) => {
    event.preventDefault();
    const selectedSlot = slotSelect.value;
    const selectedStats = statsSelect.value;

    // Only refresh if stats change
    if (selectedStats !== currentStats) {
      currentStats = selectedStats;
      refreshTable();
    }
  });

  // Initial dropdown population
  populateDropdowns(slotSelect, statsSelect);

  // Initialize on page load
  initializeFromURL();
});
