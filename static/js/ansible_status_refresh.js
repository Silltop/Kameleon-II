// Function to update the table based on fetched data
async function updatePlaybookStatus(playbookID) {
    try {
        // Fetch the latest status from the endpoint
        const response = await fetch(`/recent_run_status/${playbookID}`);
        const data = await response.json(); // Assume the response is JSON with { status: "success" }
        // Find the table row for this playbook using the ID
        const row = document.querySelector(`tr[id="${playbookID}"]`);
        if (row) {
            // Assuming the status column is in the second cell (index 1)
            const statusCell = row.cells[1];

            // Update the badge based on the new status
            statusCell.innerHTML = getStatusBadge(data.result);
        } else {
            console.warn(`Row with playbook ID ${playbookID} not found.`);
        }
    } catch (error) {
        console.error("Error updating playbook status:", error);
    }
}

// Function to return the corresponding badge HTML based on status
function getStatusBadge(status) {
    switch (status.toLowerCase()) {
        case "success":
            return '<span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Success</span>';
        case "unknown":
            return '<span class="badge badge-secondary"><i class="fa-solid fa-circle-question"></i> Unknown</span>';
        case "failed":
            return '<span class="badge badge-danger"><i class="fa-solid fa-circle-xmark"></i> Failure</span>';
        case "running":
            return '<span class="badge badge-primary"><i class="fa-solid fa-forward"></i> Running</span>';
        default:
            return '<span class="badge badge-secondary"><i class="fa-solid fa-circle-question"></i> Unknown</span>';
    }
}
