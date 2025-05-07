async function fetchJSON(url) {
    const res = await fetch(url);
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);
    try {
        return JSON.parse(text);
    } catch {
        console.error("Invalid JSON:", text);
        throw new Error("Invalid JSON response");
    }
}

let trendChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const trendBtn = document.getElementById('trendBtn');
    const ingInput = document.getElementById('ing');
    const chartCanvas = document.getElementById('trendChart');

    if (!trendBtn || !ingInput || !chartCanvas) {
        console.warn("Missing required DOM elements for charting");
        return;
    }

    btn.onclick = async () => {
        const ing = input.value.trim();


        try {
            const data = await fetchJSON(`/trends?ingredient=${encodeURIComponent(ing)}`);
            if (trendChart) trendChart.destroy();

            trendChart = new Chart(canvas.getContext("2d"), {
                type: "line",
                data: {
                    labels: data.dates,
                    datasets: [{label: ing, data: data.counts, tension: 0.3}]
                },
                options: {
                    responsive: true,
                    plugins: {legend: {display: true}}
                }
            })
            canvas.scrollIntoView({behavior: "smooth", block: "start"});

        } catch (err) {
            console.error(err);
            alert("Failed to load trend data.");
        }
    };

});
