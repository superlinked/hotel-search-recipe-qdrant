let currentOffset = 0;
let currentQuery = '';
let hasMore = true;

async function searchHotels() {
    currentOffset = 0;
    currentQuery = document.getElementById('searchInput').value.trim();
    hasMore = true;
    
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const summaryDiv = document.getElementById('summary');

    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';
    loadMoreBtn.style.display = 'none';
    summaryDiv.style.display = 'none';

    try {
        await fetchResults();
    } finally {
        loadingDiv.style.display = 'none';
    }
}

async function loadMore() {
    if (!hasMore) return;
    
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'block';
    
    try {
        await fetchResults();
    } finally {
        loadingDiv.style.display = 'none';
    }
}

async function fetchResults() {
    try {
        const searchParams = new URLSearchParams();
        if (currentQuery) searchParams.append('query', currentQuery);
        
        searchParams.append('limit', '20');
        searchParams.append('offset', currentOffset.toString());
        
        const startTime = performance.now();
        const response = await fetch(`/search?${searchParams}`);
        const responsePayload = await response.json();
        const searchTime = Math.round(performance.now() - startTime);
        
        if (!response.ok) {
            const errorDetail = responsePayload.detail || 'Search failed';
            throw new Error(errorDetail);
        }

        const data = responsePayload.results || [];
        const debugParams = responsePayload.debug_params || {};

        const debugOutputEl = document.getElementById('debugParamsOutput');
        const defaultParamsText = JSON.stringify({
            "price_weight": 0.0,
            "rating_weight": 0.0,
            "rating_count_weight": 0.0,
            "description_weight": 0.0
        }, null, 2);

        if (Object.keys(debugParams).length === 0) {
            debugOutputEl.textContent = defaultParamsText;
        } else {
            debugOutputEl.textContent = JSON.stringify(debugParams, null, 2);
        }
        
        const resultsDiv = document.getElementById('results');
        const summaryDiv = document.getElementById('summary');
        const loadMoreBtn = document.getElementById('loadMoreBtn');

        if (currentOffset === 0) {
            summaryDiv.innerHTML = `${data.length} results found in ${searchTime}ms`;
            summaryDiv.style.display = 'block';
        }

        if (data.length === 0) {
            if (currentOffset === 0) {
                resultsDiv.innerHTML = '<p style="text-align: center; grid-column: 1 / -1;">No matching items found.</p>';
                summaryDiv.style.display = 'none';
            }
            hasMore = false;
            loadMoreBtn.style.display = 'none';
        } else {
            data.forEach((result, index) => {
                const productCard = document.createElement('div');
                productCard.className = 'product-card';

                const imageHTML = `
                    <div class="card-image">
                        <img src="${result.image_src || ''}" alt="${result.id}"
                             onerror="this.onerror=null; this.src='https://via.placeholder.com/160x160?text=No+Image';">
                    </div>
                `;

                const textHTML = `
                    <div class="card-text">
                        <h3>${result.id}</h3> 
                        <div class="location">
                            <span>${result.city || 'N/A'}, ${result.country || 'N/A'}</span>
                        </div>
                        <div class="description">
                            ${result.description ? (result.description.length > 250 ? result.description.substring(0, 250) + '...' : result.description) : 'No description available.'}
                        </div>
                    </div>
                `;

                let ratingLabel = 'Okay';
                if (result.rating >= 9) ratingLabel = 'Exceptional';
                else if (result.rating >= 8) ratingLabel = 'Very Good';
                else if (result.rating >= 7) ratingLabel = 'Good';

                const ratingActionHTML = `
                    <div class="card-rating-action">
                        <div class="rating-section">
                            <div class="label">${ratingLabel}</div>
                            <div class="reviews">${result.rating_count || 0} reviews</div>
                            <div class="rating-pill">${result.rating !== undefined ? result.rating.toFixed(1) : 'N/A'}</div>
                        </div>
                        <button class="cta-button">Show prices</button>
                    </div>
                `;

                productCard.innerHTML = imageHTML + textHTML + ratingActionHTML;

                const priceButton = productCard.querySelector('.cta-button');
                if (priceButton) {
                    priceButton.onclick = (e) => {
                        e.stopPropagation();
                        showHotelDetails(result);
                    };
                }

                // Make the title clickable
                const titleElement = productCard.querySelector('h3');
                if (titleElement) {
                    titleElement.onclick = () => {
                        showHotelDetails(result);
                    };
                }
                
                resultsDiv.appendChild(productCard);
            });

            currentOffset += data.length;
            loadMoreBtn.style.display = data.length === 20 ? 'inline-block' : 'none';
            hasMore = data.length === 20;
        }
    } catch (error) {
        const resultsDiv = document.getElementById('results');
        const summaryDiv = document.getElementById('summary');
        resultsDiv.innerHTML = `<p style="text-align: center; grid-column: 1 / -1;">Error: ${error.message}</p>`;
        summaryDiv.style.display = 'none';
    }
}

window.addEventListener('scroll', () => {
    if (!hasMore) return;
    
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 5) {
        loadMore();
    }
});

document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchHotels();
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    searchHotels();

    // Add click listeners for search suggestions
    document.querySelectorAll('.search-suggestions a').forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default anchor behavior
            const suggestionText = event.target.getAttribute('data-suggestion');
            const searchInput = document.getElementById('searchInput');
            searchInput.value = suggestionText; // Put suggestion in search box
            searchHotels(); // Trigger search
        });
    });

    // Add click listener for reset button
    document.getElementById('resetSearchBtn').addEventListener('click', () => {
        document.getElementById('searchInput').value = ''; // Clear search input
        searchHotels(); // Trigger default search
    });
});

function showHotelDetails(result) {
    const modal = document.getElementById('productModal');
    const modalImg = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalDesc = document.getElementById('modalDescription');
    const modalPrice = document.getElementById('modalPrice');
    const modalRating = document.getElementById('modalRating');
    const modalRatingCount = document.getElementById('modalRatingCount');
    const modalCity = document.getElementById('modalCity');
    const modalCountry = document.getElementById('modalCountry');
    const modalAmenities = document.getElementById('modalAmenities');

    modalImg.src = result.image_src || '';
    modalImg.onerror = () => {
        modalImg.src = 'https://via.placeholder.com/400x533?text=Image+Not+Available';
    };
    modalTitle.textContent = result.id;
    modalDesc.textContent = result.description || 'No description provided.';
    modalPrice.textContent = (result.price !== undefined && result.price !== null) ? result.price.toFixed(2) : 'N/A';
    
    modalRating.textContent = (result.rating !== undefined && result.rating !== null) ? result.rating.toFixed(1) : 'N/A';
    modalRatingCount.textContent = result.rating_count || 0;
    modalCity.textContent = result.city || 'N/A';
    modalCountry.textContent = result.country || 'N/A';

    const allAmenities = [
        ...(result.property_amenities || []),
        ...(result.room_amenities || []),
        ...(result.wellness_spa || []),
        ...(result.accessibility || []),
        ...(result.for_children || [])
    ];
    modalAmenities.innerHTML = allAmenities.length > 0 
        ? allAmenities.map(a => `<li>${a}</li>`).join('') 
        : '<li>No amenities listed.</li>';

    modal.style.display = 'block';
}

document.querySelector('.close').onclick = function() {
    document.getElementById('productModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('productModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
} 