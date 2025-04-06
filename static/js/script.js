document.addEventListener('DOMContentLoaded', function() {
    const queryForm = document.getElementById('queryForm');
    const loadingDiv = document.querySelector('.loading');
    const resultContainer = document.getElementById('resultContainer');
    const sqlQueryDiv = document.getElementById('sqlQuery');
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');
    const errorMessage = document.getElementById('errorMessage');
    const exampleQueries = document.querySelectorAll('.example-query');
    
    // Handle example query clicks
    exampleQueries.forEach(query => {
        query.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('nlQuery').value = this.textContent;
        });
    });
    
    queryForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const query = document.getElementById('nlQuery').value;
        if (!query) return;
        
        // Reset previous results
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        resultContainer.style.display = 'none';
        
        // Show loading indicator
        loadingDiv.style.display = 'block';
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred');
            }
            
            // Display SQL query
            sqlQueryDiv.textContent = data.sql_query;
            
            // Create table headers
            if (data.results && data.results.length > 0) {
                const headers = Object.keys(data.results[0]);
                tableHead.innerHTML = `
                    <tr>
                        ${headers.map(header => `<th>${header}</th>`).join('')}
                    </tr>
                `;
                
                // Create table rows
                tableBody.innerHTML = data.results.map(row => `
                    <tr>
                        ${headers.map(header => `<td>${row[header] !== null ? row[header] : 'NULL'}</td>`).join('')}
                    </tr>
                `).join('');
                
                resultContainer.style.display = 'block';
            } else {
                tableHead.innerHTML = '';
                tableBody.innerHTML = '<tr><td colspan="100%" class="text-center">No results found</td></tr>';
                resultContainer.style.display = 'block';
            }
            
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        } finally {
            loadingDiv.style.display = 'none';
        }
    });
});