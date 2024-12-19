// Preload images and background setup
const preloadImage = "https://i.pinimg.com/originals/e1/70/03/e17003d3a86823bea8a48e4ec03d33e9.gif";

const weatherImages = [
    "https://i.pinimg.com/736x/55/41/08/55410835d2ea4e373b30ae7932bb95f0.jpg",
    "https://i.pinimg.com/736x/eb/16/66/eb1666747aef57e5d60e07e095e0683f.jpg",
    "https://i.pinimg.com/736x/29/38/4e/29384e0b1c1adbbd307c712496cf961d.jpg",
    "https://i.pinimg.com/736x/38/38/03/383803550dc373e6389ab06dc695ae97.jpg",
    "https://i.pinimg.com/736x/72/a1/e2/72a1e296a9ee6b93b8b9e6ff15e4c4f4.jpg",
    "https://i.pinimg.com/736x/c4/01/39/c401399ef4b686b2d6edfba1c3eb7bd8.jpg",
    "https://i.pinimg.com/736x/53/ac/7a/53ac7a6e725ccda99905052a2c16500d.jpg",
    "https://i.pinimg.com/736x/e1/09/6f/e1096f535670930e4a55b9d6fe157770.jpg"
];

let lastImageIndex = -1;
let preloadedImages = [];

// Preload all images (including the preload image)
function preloadImages() {
    const preload = new Image();
    preload.src = preloadImage;

    weatherImages.forEach(imageUrl => {
        const img = new Image();
        img.src = imageUrl;
        preloadedImages.push(img); // Store preloaded images
    });
}

// Set a specific image on page load
function setInitialBackground() {
    document.body.style.backgroundImage = `url(${preloadImage})`;
    document.body.style.backgroundSize = "cover";
    document.body.style.backgroundPosition = "center";
    document.body.style.backgroundAttachment = "fixed";
}

// Change to a random background image (excluding the preload image)
function changeBackgroundImage() {
    let randomIndex;

    // Ensure that the image is not repeated consecutively
    do {
        randomIndex = Math.floor(Math.random() * preloadedImages.length);
    } while (randomIndex === lastImageIndex);

    lastImageIndex = randomIndex;
    const selectedImage = preloadedImages[randomIndex].src;

    // Set the background image from the preloaded images
    document.body.style.backgroundImage = `url(${selectedImage})`;
    document.body.style.backgroundSize = "cover";
    document.body.style.backgroundPosition = "center";
    document.body.style.backgroundAttachment = "fixed";
}

// Fetch weather data when the button is clicked
document.getElementById('fetch-weather-btn').addEventListener('click', async () => {
    const city = document.getElementById('city-input').value.trim();

    if (!city) {
        alert("Please enter a city name.");
        return;  // Stop if city is not provided
    }

    try {
        // Fetch weather data
        const weatherResponse = await fetch(`http://localhost:5000/weather?city=${city}`);
        const weatherData = await weatherResponse.json();

        if (weatherData.error) {
            console.error("Error fetching weather data:", weatherData.error);
            alert(weatherData.error);
        } else {
            // Display the weather data
            displayWeatherData(weatherData);
        }

        // Fetch forecast/trends data
        const forecastResponse = await fetch(`http://localhost:5000/forecast?city=${city}`);
        const forecastData = await forecastResponse.json();

        if (forecastData.error) {
            console.error("Error fetching forecast data:", forecastData.error);
            alert(forecastData.error);
        } else {
            // Display the 5 graphs
            displayGraph('hot-weather-graph', forecastData.hot_weather_graph);
            displayGraph('cold-weather-graph', forecastData.cold_weather_graph);
            displayGraph('future-precipitation-graph', forecastData.future_precipitation_graph);
            displayGraph('future-humidity-graph', forecastData.future_humidity_graph);
            displayGraph('future-temperature-graph', forecastData.future_temperature_graph);

            // Change background image after graphs load
            changeBackgroundImage();
        }
    } catch (error) {
        console.error("Request failed:", error);
        alert("Failed to fetch data. Please try again.");
    }
});

// Function to display weather data (including avg temperature, humidity, and precipitation)
function displayWeatherData(data) {
    // Ensure data keys match the backend's response format
    document.getElementById('city-name').innerText = `City: ${data.city || "N/A"}`;
    document.getElementById('temperature').innerText = `Average Temperature: ${data.avg_temp !== undefined ? data.avg_temp + " °C" : "N/A"}`;
    document.getElementById('rainfall').innerText = `Precipitation: ${data.precipitation !== undefined ? data.precipitation + " mm" : "N/A"}`;
    document.getElementById('humidity').innerText = `Humidity: ${data.humidity !== undefined ? data.humidity + "%" : "N/A"}`;

    // Heatwave and cold winter detection
    const avgTemp = parseFloat(data.avg_temp);
    document.getElementById('heat-waves').innerText = avgTemp > 29 ? "Heat Wave: Yes" : "Heat Wave: No";
    document.getElementById('cold-winter').innerText = avgTemp < 11 ? "Cold Winter: Yes" : "Cold Winter: No";
}

// Function to display graphs
function displayGraph(graphId, graphData) {
    const graphContainer = document.getElementById(graphId);

    // Check if the graph container exists
    if (graphContainer) {
        // Check if the graph data is valid and base64-encoded
        if (graphData && typeof graphData === "string" && graphData.length > 0) {
            const img = document.createElement('img');
            img.src = 'data:image/png;base64,' + graphData;  // Assuming the backend returns the graph data as a base64 string
            img.style.width = "100%";
            img.style.marginTop = "20px";
            graphContainer.innerHTML = "";  // Clear previous graph
            graphContainer.appendChild(img);
        } else {
            console.error("No graph data found for", graphId);
            graphContainer.innerHTML = "No data available for this graph.";
        }
    } else {
        console.error(`Element with id ${graphId} not found.`);
    }
}

// Preload images and set the initial background on page load
window.onload = function () {
    preloadImages();
    setInitialBackground();
};
