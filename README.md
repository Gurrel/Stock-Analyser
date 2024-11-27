
<h1>Stock Analyser</h1>

https://github.com/user-attachments/assets/c44d59ca-736d-4224-849a-df855be4a338



<p>
    This Python project provides tools for technical and fundamental analysis of stocks. It leverages the 
    <a href="https://polygon.io/" target="_blank">Polygon.io</a> API to retrieve stock data and enables 
    insights into stock performance through metrics such as beta value, stock return, price extremes, and more.
</p>

<h2>Features</h2>
<ul>
    <li>Retrieve and calculate technical metrics (e.g., beta value, stock return, highest/lowest prices).</li>
    <li>Fetch fundamental data like P/E ratio, P/S ratio, and equity ratio using Polygon.io.</li>
    <li>Analyze S&P 500 stocks with automated symbol validation from Wikipedia data.</li>
    <li>Rate-limiting management for API requests to avoid exceeding limits.</li>
    <li>Interactive GUI built using <code>tkinter</code> for user-friendly navigation.</li>
</ul>

<h2>Installation</h2>
<p>Follow these steps to set up the project:</p>
<ol>
    <li>Clone the repository:
        <pre><code>git clone https://github.com/your-username/Stock-Analyser.git</code></pre>
    </li>
    <li>Install the required Python packages:
        <pre><code>pip install requests pandas</code></pre>
    </li>
    <li>Ensure your system has access to Python 3.7 or higher.</li>
    <li>Replace the placeholder API key (<code>API_KEY</code>) with your own from 
        <a href="https://polygon.io/" target="_blank">Polygon.io</a>.
    </li>
</ol>

<h2>Usage</h2>
<p>Run the script to launch the GUI:</p>
<pre><code>python stockAnalyser.py</code></pre>
<p>In the GUI, you can:</p>
<ul>
    <li>Perform technical analysis on a stock.</li>
    <li>Perform fundamental analysis on a stock.</li>
    <li>Sort stocks by beta value.</li>
</ul>

<h2>Project Structure</h2>
<ul>
    <li><code>main.py</code>: The primary script containing the logic and GUI.</li>
    <li><code>getBusinessDayDates.py</code>: Helper script to compute business day ranges.</li>
    <li><code>requirements.txt</code>: List of Python dependencies.</li>
</ul>

<h2>API Rate Limiting</h2>
<p>
    The Polygon.io API enforces a rate limit of 5 requests per minute for free-tier users. The script includes 
    mechanisms to detect rate-limit violations and prompts users to wait before retrying.
</p>

<h2>Limitations</h2>
<ul>
    <li>Requires an active internet connection to fetch data from Polygon.io and Wikipedia.</li>
    <li>Limited to analyzing stocks within the S&P 500 index.</li>
</ul>

<h2>Author</h2>
<p>Created by Gustav Lundborg.</p>
