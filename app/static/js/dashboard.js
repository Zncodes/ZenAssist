
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // DATE AND CURRENCY
    // =====================================

    const today = new Date();

    const dateElement = document.getElementById("current-date");

    if (dateElement) {
        dateElement.textContent = today.toLocaleDateString(
            "en-US",
            {
                weekday: "short",
                day: "numeric",
                month: "short",
                year: "numeric",
                timeZone: "Asia/Jakarta"
            }
        );
    }

    const dateParts = new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "numeric",
        timeZone: "Asia/Jakarta"
    }).formatToParts(today);

    const currentMonth = Number(
        dateParts.find(part => part.type === "month").value
    );

    const currentYear = Number(
        dateParts.find(part => part.type === "year").value
    );

    const currencyFormatter = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0
    });

    function formatRupiah(amount) {
        return currencyFormatter.format(Number(amount) || 0);
    }


    // =====================================
    // API HELPER
    // =====================================

    async function fetchAPI(url) {

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(
                `API request failed: ${response.status}`
            );
        }

        return await response.json();
    }


    // =====================================
    // UI HELPER
    // =====================================

    function updateElement(id, value) {

        const element = document.getElementById(id);

        if (element) {
            element.textContent = value;
        }
    }

    function showError(ids, message = "Unable to load data") {

        ids.forEach(id => {
            updateElement(id, message);
        });
    }


    // =====================================
    // TASKS
    // =====================================

    async function loadTasks() {

        try {

            const data = await fetchAPI("/api/tasks/");

            // Support direct array or wrapped response
            const tasks = Array.isArray(data)
                ? data
                : (data.tasks || data.items || []);

            const totalTasks = tasks.length;

            const completedTasks = tasks.filter(
                task => task.status === "completed"
            ).length;

            const pendingTasks = totalTasks - completedTasks;

            const inProgressTasks = tasks.filter(
                task => task.status === "in_progress"
            ).length;

            updateElement("total-tasks", totalTasks);

            updateElement(
                "tasks-description",
                `${pendingTasks} pending · ${inProgressTasks} in progress`
            );

        } catch (error) {

            console.error("Tasks API Error:", error);

            showError(
                ["total-tasks", "tasks-description"]
            );
        }
    }


    // =====================================
    // FINANCE OVERVIEW
    // =====================================

    async function loadFinance() {

        try {

            const url =
                `/api/finance/dashboard/overview?month=${currentMonth}&year=${currentYear}`;

            const data = await fetchAPI(url);

            updateElement(
                "monthly-income",
                formatRupiah(data.total_income)
            );

            updateElement(
                "monthly-expenses",
                formatRupiah(data.total_expense)
            );

            updateElement(
                "income-description",
                "Income this month"
            );

            updateElement(
                "expenses-description",
                "Expenses this month"
            );

        } catch (error) {

            console.error("Finance API Error:", error);

            showError([
                "monthly-income",
                "monthly-expenses",
                "income-description",
                "expenses-description"
            ]);
        }
    }


    // =====================================
    // SAVINGS OVERVIEW
    // =====================================

    async function loadSavings() {

        try {

            const data = await fetchAPI(
                "/api/finance/dashboard/savings"
            );

            updateElement(
                "savings-goals",
                data.goals_count
            );

            updateElement(
                "savings-description",
                `${formatRupiah(data.total_saved)} saved`
            );

        } catch (error) {

            console.error("Savings API Error:", error);

            showError([
                "savings-goals",
                "savings-description"
            ]);
        }
    }


    // =====================================
    // INITIALIZE DASHBOARD
    // =====================================

    async function initializeDashboard() {

        await Promise.allSettled([
            loadTasks(),
            loadFinance(),
            loadSavings()
        ]);

        console.log("ZenAssist Dashboard loaded.");
    }

    initializeDashboard();

});
