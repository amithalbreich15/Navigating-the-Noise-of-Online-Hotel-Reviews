async function scrapeReviews() {
    let allReviews = [];
    const totalPages = getTotalPages();
    const textDecoder = new TextDecoder('utf-8');

    async function scrapePage() {
        const reviewCards = document.querySelectorAll('[data-testid="review-card"]');
        const overallAverageRatingElement = document.querySelector('[data-testid="review-score-component"]');
        const overallAverageRating = overallAverageRatingElement ? overallAverageRatingElement.textContent.trim().match(/\d+(\.\d+)?/)[0] : '';

        reviewCards.forEach(card => {
            const reviewTitleElement = card.querySelector('[data-testid="review-title"]');
            const negativeReviewElement = card.querySelector('[data-testid="review-negative-text"]');
            const positiveReviewElement = card.querySelector('[data-testid="review-positive-text"]');
            const overallRatingElement = card.querySelector('[data-testid="review-score"]');
            const stayDateElement = card.querySelector('[data-testid="review-stay-date"]');
            const dateOfReviewElement = card.querySelector('[data-testid="review-date"]');
            const roomTypeElement = card.querySelector('[data-testid="review-room-name"]');
            const numNightsElement = card.querySelector('[data-testid="review-num-nights"]');
            const travelerTypeElement = card.querySelector('[data-testid="review-traveler-type"]');

            const reviewTitle = reviewTitleElement ? decodeText(reviewTitleElement.textContent.trim()) : '';
            const negativeReview = negativeReviewElement ? decodeText(negativeReviewElement.textContent.trim()) : '';
            const positiveReview = positiveReviewElement ? decodeText(positiveReviewElement.textContent.trim()) : '';
            const overallRating = overallRatingElement ? overallRatingElement.textContent.trim().match(/\d+(\.\d+)?/)[0] : '';
            const stayDate = stayDateElement ? decodeText(stayDateElement.textContent.trim()) : '';
            const dateOfReview = dateOfReviewElement ? decodeText(dateOfReviewElement.textContent.replace('Reviewed: ', '').trim()) : '';
            const roomType = roomTypeElement ? decodeText(roomTypeElement.textContent.trim()) : '';
            const numNights = numNightsElement ? decodeText(numNightsElement.textContent.trim().split(' ')[0]) : '';
            const travelerType = travelerTypeElement ? decodeText(travelerTypeElement.textContent.trim()) : '';

            allReviews.push({
                reviewTitle,
                negativeReview,
                positiveReview,
                overallRating,
                stayDate,
                dateOfReview,
                roomType,
                numNights,
                travelerType,
                overallAverageRating
            });
        });
    }

    for (let page = 1; page <= totalPages; page++) {
        await scrapePage();
        const nextPageButton = document.querySelector('button[aria-label="Next page"]');
        if (nextPageButton && page < totalPages) {
            nextPageButton.click();
            await new Promise(r => setTimeout(r, 3000)); // Wait for the next page to load
        }
    }

    let csvContent = "Review Title,Negative Reviews,Positive Reviews,Rating,Stay Date,Review Date,Room Type,Number of Nights,Traveler Type,Overall Average Rating\n";
    allReviews.forEach(review => {
        csvContent += [
            escapeCSVField(review.reviewTitle),
            escapeCSVField(review.negativeReview),
            escapeCSVField(review.positiveReview),
            escapeCSVField(review.overallRating),
            escapeCSVField(review.stayDate),
            escapeCSVField(review.dateOfReview),
            escapeCSVField(review.roomType),
            escapeCSVField(review.numNights),
            escapeCSVField(review.travelerType),
            escapeCSVField(review.overallAverageRating)
        ].join(",") + "\n";
    });

    const hotelName = extractHotelName();
    downloadCSV(`reviews_${hotelName}`, csvContent);
}

function getTotalPages() {
    const paginationContainer = document.querySelector('div[role="navigation"] ol');
    if (!paginationContainer) {
        console.log("Pagination container not found.");
        return 1;
    }

    const pageItems = paginationContainer.querySelectorAll('li button');
    const pageNumbers = Array.from(pageItems).map(item => parseInt(item.textContent.trim())).filter(number => !isNaN(number));
    const totalPages = pageNumbers.length > 0 ? Math.max(...pageNumbers) : 1;
    console.log("Total pages:", totalPages);

    return totalPages;
}

function extractHotelName() {
    const hotelNameElement = document.querySelector('h2.pp-header__title');
    return hotelNameElement ? hotelNameElement.textContent.trim().replace(/\s+/g, '_') : 'unknown_hotel';
}

function decodeText(text) {
    const textDecoder = new TextDecoder('utf-8');
    const bytes = new TextEncoder().encode(text);
    return textDecoder.decode(bytes);
}

function escapeCSVField(field) {
    if (field.includes(',') || field.includes('"') || field.includes('\n')) {
        return `"${field.replace(/"/g, '""')}"`;
    }
    return field;
}

function downloadCSV(fileName, csvContent) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${fileName}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

scrapeReviews();