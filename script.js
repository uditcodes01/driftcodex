document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // DRIFTCODEX.TECH — DYNAMIC AI ROUTE OPTIMIZATION
    // =========================================================

    const button = document.getElementById("optimizeButton");

    const status = document.getElementById("aiStatus");
    const message = document.getElementById("aiMessage");

    const decisionBox = document.getElementById("decisionBox");
    const decisionTitle = document.getElementById("decisionTitle");
    const decisionText = document.getElementById("decisionText");

    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");
    const progressPercent = document.getElementById("progressPercent");

    const mapContainer = document.querySelector(".map-container");

    // Pipeline stages
    const stepIce = document.getElementById("stepIce");
    const stepWeather = document.getElementById("stepWeather");
    const stepHazard = document.getElementById("stepHazard");
    const stepAI = document.getElementById("stepAI");
    const stepRoute = document.getElementById("stepRoute");

    const steps = [
        stepIce,
        stepWeather,
        stepHazard,
        stepAI,
        stepRoute
    ];

    // ---------------------------------------------------------
    // REAL PROJECT RESULTS
    // ---------------------------------------------------------

    const finalResults = {
        averageRisk: 7.04,
        maximumRisk: 48.21,
        dangerous: 0,
        critical: 0,
        routeCells: 1119
    };


    // =========================================================
    // INITIAL SYSTEM STATE
    // =========================================================

    function initializeSystem() {

        status.innerHTML = "READY";
        status.className = "ai-status";

        message.innerHTML =
            "AI navigation system is ready to analyze Antarctic environmental conditions.";

        decisionTitle.innerHTML = "AWAITING AI ANALYSIS";

        decisionText.innerHTML =
            "Press RUN AI OPTIMIZATION to begin environmental analysis.";

        button.disabled = false;
        button.innerHTML = "🚀 RUN AI OPTIMIZATION";

        progressFill.style.width = "0%";
        progressText.innerHTML = "SYSTEM READY";
        progressPercent.innerHTML = "0%";

        clearPipeline();

        if (decisionBox) {
            decisionBox.classList.remove("optimizing");
        }

        if (mapContainer) {
            mapContainer.classList.remove("optimizing");
            mapContainer.classList.remove("optimized");
        }
    }


    // =========================================================
    // PROGRESS BAR
    // =========================================================

    function setProgress(percent, text) {

        if (progressFill) {
            progressFill.style.width = percent + "%";
        }

        if (progressPercent) {
            progressPercent.innerHTML = percent + "%";
        }

        if (progressText) {
            progressText.innerHTML = text;
        }
    }


    // =========================================================
    // PIPELINE CONTROL
    // =========================================================

    function clearPipeline() {

        steps.forEach(function (step) {

            if (!step) return;

            step.classList.remove("active");
            step.classList.remove("complete");

        });
    }


    function activateStep(step) {

        if (!step) return;

        step.classList.add("active");
        step.classList.remove("complete");
    }


    function completeStep(step) {

        if (!step) return;

        step.classList.remove("active");
        step.classList.add("complete");
    }


    // =========================================================
    // TYPEWRITER EFFECT
    // =========================================================

    function typeMessage(element, text, speed = 18) {

        if (!element) return;

        element.innerHTML = "";

        let index = 0;

        const interval = setInterval(function () {

            element.innerHTML += text.charAt(index);

            index++;

            if (index >= text.length) {
                clearInterval(interval);
            }

        }, speed);
    }


    // =========================================================
    // NUMBER COUNTER
    // =========================================================

    function animateNumber(element, start, end, duration, decimals = 0) {

        if (!element) return;

        const startTime = performance.now();

        function update(currentTime) {

            const elapsed = currentTime - startTime;

            const progress = Math.min(elapsed / duration, 1);

            // Smooth easing
            const eased =
                1 - Math.pow(1 - progress, 3);

            const value =
                start + (end - start) * eased;

            element.innerHTML =
                value.toFixed(decimals);

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }


    // =========================================================
    // OPTIMIZATION START
    // =========================================================

    function startOptimization() {

        // Prevent double clicks
        if (button.disabled) return;

        button.disabled = true;

        clearPipeline();

        // ---------------------------------------------
        // START STATE
        // ---------------------------------------------

        status.innerHTML = "ANALYZING";
        status.className = "ai-status analyzing";

        button.innerHTML =
            "🛰️ INITIALIZING AI...";

        typeMessage(
            message,
            "Initializing Antarctic environmental intelligence engine..."
        );

        decisionTitle.innerHTML =
            "INITIALIZING ANALYSIS";

        decisionText.innerHTML =
            "Loading sea-ice, weather and iceberg hazard layers.";

        setProgress(
            5,
            "INITIALIZING AI ENGINE"
        );

        if (mapContainer) {
            mapContainer.classList.add("optimizing");
            mapContainer.classList.remove("optimized");
        }

        activateStep(stepIce);


        // =================================================
        // STAGE 1 — SEA ICE
        // =================================================

        setTimeout(function () {

            button.innerHTML =
                "❄️ ANALYZING SEA ICE...";

            status.innerHTML =
                "ICE ANALYSIS";

            typeMessage(
                message,
                "Scanning Antarctic sea-ice concentration and identifying high-risk ice regions..."
            );

            decisionTitle.innerHTML =
                "SEA-ICE ANALYSIS";

            decisionText.innerHTML =
                "Evaluating ice concentration across the navigation grid.";

            setProgress(
                22,
                "ANALYZING SEA-ICE CONDITIONS"
            );

        }, 900);


        // =================================================
        // STAGE 2 — WEATHER
        // =================================================

        setTimeout(function () {

            completeStep(stepIce);
            activateStep(stepWeather);

            button.innerHTML =
                "🌊 ANALYZING WEATHER...";

            status.innerHTML =
                "WEATHER ANALYSIS";

            typeMessage(
                message,
                "Processing wind conditions and identifying regions with elevated weather risk..."
            );

            decisionTitle.innerHTML =
                "WEATHER RISK MODEL";

            decisionText.innerHTML =
                "Calculating wind-based navigation risk from ERA5 environmental data.";

            setProgress(
                42,
                "CALCULATING WEATHER RISK"
            );

        }, 2200);


        // =================================================
        // STAGE 3 — ICEBERG HAZARDS
        // =================================================

        setTimeout(function () {

            completeStep(stepWeather);
            activateStep(stepHazard);

            button.innerHTML =
                "⚠️ ANALYZING ICEBERG HAZARDS...";

            status.innerHTML =
                "HAZARD ANALYSIS";

            typeMessage(
                message,
                "Detecting iceberg hazards and generating spatial hazard-risk zones..."
            );

            decisionTitle.innerHTML =
                "ICEBERG HAZARD DETECTION";

            decisionText.innerHTML =
                "Mapping detected iceberg hazards and calculating spatial avoidance costs.";

            setProgress(
                61,
                "MAPPING ICEBERG HAZARDS"
            );

        }, 3500);


        // =================================================
        // STAGE 4 — AI RISK FUSION
        // =================================================

        setTimeout(function () {

            completeStep(stepHazard);
            activateStep(stepAI);

            button.innerHTML =
                "🧠 FUSING RISK LAYERS...";

            status.innerHTML =
                "AI RISK FUSION";

            typeMessage(
                message,
                "Fusing ice, weather and iceberg intelligence into a unified navigation risk model..."
            );

            decisionTitle.innerHTML =
                "3-LAYER RISK MODEL";

            decisionText.innerHTML =
                "Combining environmental hazards using weighted AI risk scoring.";

            setProgress(
                76,
                "FUSING ENVIRONMENTAL RISK"
            );

        }, 4900);


        // =================================================
        // STAGE 5 — A* ROUTE OPTIMIZATION
        // =================================================

        setTimeout(function () {

            completeStep(stepAI);
            activateStep(stepRoute);

            status.innerHTML =
                "OPTIMIZING";

            status.className =
                "ai-status optimizing";

            button.innerHTML =
                "🧭 CALCULATING SAFEST ROUTE...";

            typeMessage(
                message,
                "Running risk-aware A* pathfinding to identify the safest navigable corridor..."
            );

            decisionTitle.innerHTML =
                "ROUTE OPTIMIZATION";

            decisionText.innerHTML =
                "Searching thousands of grid cells while avoiding dangerous and critical regions.";

            setProgress(
                88,
                "RUNNING RISK-AWARE A*"
            );

        }, 6100);


        // =================================================
        // ROUTE SEARCH ANIMATION
        // =================================================

        setTimeout(function () {

            setProgress(
                94,
                "EVALUATING ROUTE CANDIDATES"
            );

            button.innerHTML =
                "🔎 EVALUATING ROUTE...";

            typeMessage(
                message,
                "Comparing candidate paths and selecting the lowest-risk navigable corridor..."
            );

        }, 7200);


        // =================================================
        // FINAL RESULT
        // =================================================

        setTimeout(function () {

            completeStep(stepRoute);

            if (mapContainer) {
                mapContainer.classList.remove("optimizing");
                mapContainer.classList.add("optimized");
            }

            status.innerHTML =
                "LOW RISK";

            status.className =
                "ai-status low-risk";

            button.innerHTML =
                "✅ ROUTE OPTIMIZED";

            typeMessage(
                message,
                "AI analysis complete. The optimized route successfully avoids dangerous and critical regions."
            );

            decisionTitle.innerHTML =
                "OPTIMAL ROUTE IDENTIFIED";

            decisionText.innerHTML =
                "Average Risk: " +
                finalResults.averageRisk.toFixed(2) +
                "/100 • Maximum Risk: " +
                finalResults.maximumRisk.toFixed(2) +
                "/100 • Dangerous: " +
                finalResults.dangerous +
                " • Critical: " +
                finalResults.critical;

            setProgress(
                100,
                "OPTIMIZATION COMPLETE"
            );

            // ---------------------------------------------
            // Small result reveal delay
            // ---------------------------------------------

            setTimeout(function () {

                button.disabled = false;

                button.innerHTML =
                    "🚀 RUN AI OPTIMIZATION";

            }, 4500);

        }, 8500);
    }


    // =========================================================
    // BUTTON EVENT
    // =========================================================

    if (button) {

        button.addEventListener(
            "click",
            startOptimization
        );

    } else {

        console.error(
            "DRIFTCODEX: optimizeButton not found."
        );

    }


    // =========================================================
    // START IN READY STATE
    // =========================================================

    initializeSystem();

});