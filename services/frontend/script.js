document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM content loaded");
    // Set slider to middle (0.5) when page is refreshed
    document.getElementById("alpha").value = 0.5;
    updateSliderValuePosition();
});

function updateAlphaValue(value) {
    document.getElementById("alpha").value = value;
    document.querySelector(".slider-value").innerText = value;
    updateSliderValuePosition();
}

function updateSliderValuePosition() {
    console.log("Updating slider value position");
    const slider = document.getElementById("alpha");
    const sliderValue = document.querySelector(".slider-value");
    const sliderWidth = slider.offsetWidth;
    const sliderThumbWidth = slider.querySelector("::-webkit-slider-thumb").offsetWidth;
    const value = parseFloat(slider.value);
    const position = (value * (sliderWidth - sliderThumbWidth));
    console.log("Slider width:", sliderWidth);
    console.log("Thumb width:", sliderThumbWidth);
    console.log("Slider value:", value);
    console.log("Position:", position);
    sliderValue.style.left = `${position}px`;

    // Update slider value display
    sliderValue.innerText = slider.value;
}
function clearSearch() {
    document.getElementById('query').value = ''; // Clear the search input field
}


function myFunction() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}


async function sendQuery() {
    const query = document.getElementById("query").value;
    const alpha = document.getElementById("alpha").value;
    const payload = {
      query: `{
        Get {
          Recipes(
            limit: 3
            hybrid: {
              query: "${query}"
              properties: [\"ner_new\"]
              alpha: ${alpha}
            }
          ) {
            title,
            link
          }
        }
      }`
    };

    try {
        const response = await fetch('http://localhost:8080/v1/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayResults(result) {
  const resultContainer = document.getElementById('result');
  resultContainer.innerHTML = '';

  if (result.data && result.data.Get && result.data.Get.Recipes) {
      result.data.Get.Recipes.forEach(recipe => {
          // Prepend https:// to the recipe link if it doesn't already have it
          const link = recipe.link.startsWith('https://') ? recipe.link : `https://${recipe.link}`;

          const recipeElement = document.createElement('div');
          recipeElement.className = 'recipe';
          recipeElement.innerHTML = `
              <h2><a href="${link}" target="_blank">${recipe.title} 🔗</a></h2>
          `;
          resultContainer.appendChild(recipeElement);
      });
  } else {
      resultContainer.innerHTML = '<p>No results found</p>';
  }
}

