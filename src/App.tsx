import { useState } from 'react';

function App() {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const CodeBlock = ({ code, id }: { code: string; id: string }) => (
    <div className="relative group">
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
        <code>{code}</code>
      </pre>
      <button
        onClick={() => copyToClipboard(code, id)}
        className="absolute top-2 right-2 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {copied === id ? '✓ Copied' : 'Copy'}
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🎯</span>
            <div>
              <h1 className="text-2xl font-bold text-white">Shopify Niche Intelligence</h1>
              <p className="text-purple-300 text-sm">Python + Streamlit Application</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Discover Profitable Shopify Niches
          </h2>
          <p className="text-xl text-purple-200 max-w-3xl mx-auto mb-8">
            A powerful research tool for finding profitable niches, analyzing Shopify stores, 
            and discovering trending products — all with transparent, verified data.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <span className="px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-full text-green-300 text-sm">
              ✅ Only Verified Shopify Stores
            </span>
            <span className="px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-blue-300 text-sm">
              📊 Transparent Scoring
            </span>
            <span className="px-4 py-2 bg-purple-500/20 border border-purple-500/50 rounded-full text-purple-300 text-sm">
              🛒 GMC Analysis
            </span>
          </div>
        </div>

        {/* Alert Box */}
        <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-xl p-6 mb-12">
          <div className="flex items-start gap-4">
            <span className="text-3xl">⚠️</span>
            <div>
              <h3 className="text-xl font-semibold text-yellow-300 mb-2">
                This is a Python/Streamlit Application
              </h3>
              <p className="text-yellow-200">
                This tool is built with Python and Streamlit, not React. To use it, you need to:
              </p>
              <ol className="mt-3 space-y-2 text-yellow-100">
                <li className="flex items-center gap-2">
                  <span className="flex-shrink-0 w-6 h-6 bg-yellow-500/30 rounded-full flex items-center justify-center text-sm">1</span>
                  Download the <code className="bg-black/30 px-2 py-0.5 rounded">shopify-niche-intelligence</code> folder
                </li>
                <li className="flex items-center gap-2">
                  <span className="flex-shrink-0 w-6 h-6 bg-yellow-500/30 rounded-full flex items-center justify-center text-sm">2</span>
                  Upload it to your GitHub repository
                </li>
                <li className="flex items-center gap-2">
                  <span className="flex-shrink-0 w-6 h-6 bg-yellow-500/30 rounded-full flex items-center justify-center text-sm">3</span>
                  Deploy on Streamlit Cloud
                </li>
              </ol>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {[
            { icon: '🎯', title: 'Niche Discovery', desc: 'Find profitable niches with intelligent 0-100 scoring' },
            { icon: '🔥', title: 'Trending Analysis', desc: 'Discover trending opportunities across categories' },
            { icon: '📦', title: 'Product Finder', desc: 'Search products from verified Shopify stores' },
            { icon: '🏪', title: 'Store Discovery', desc: 'Find and analyze verified Shopify stores only' },
            { icon: '🛒', title: 'GMC Suitability', desc: 'Check Google Merchant Center compatibility' },
            { icon: '📊', title: 'Export Data', desc: 'Export results to CSV, Excel, or JSON' },
          ].map((feature, i) => (
            <div key={i} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <span className="text-4xl mb-4 block">{feature.icon}</span>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.desc}</p>
            </div>
          ))}
        </div>

        {/* Installation Steps */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 mb-12">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span>🚀</span> Quick Start Guide
          </h3>

          <div className="space-y-8">
            {/* Step 1 */}
            <div>
              <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center gap-2">
                <span className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-sm">1</span>
                Clone or Download Files
              </h4>
              <p className="text-gray-400 mb-3">
                Copy the <code className="bg-black/30 px-2 py-0.5 rounded text-purple-300">shopify-niche-intelligence</code> folder to your local machine.
              </p>
            </div>

            {/* Step 2 */}
            <div>
              <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center gap-2">
                <span className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-sm">2</span>
                Create GitHub Repository
              </h4>
              <CodeBlock
                id="git"
                code={`cd shopify-niche-intelligence
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main`}
              />
            </div>

            {/* Step 3 */}
            <div>
              <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center gap-2">
                <span className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-sm">3</span>
                Deploy on Streamlit Cloud
              </h4>
              <ol className="text-gray-400 space-y-2 ml-4">
                <li>1. Go to <a href="https://share.streamlit.io" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300 underline">share.streamlit.io</a></li>
                <li>2. Click "New app"</li>
                <li>3. Select your repository</li>
                <li>4. Set main file path: <code className="bg-black/30 px-2 py-0.5 rounded text-purple-300">app.py</code></li>
                <li>5. Click "Deploy"</li>
              </ol>
            </div>

            {/* Step 4 - Local */}
            <div>
              <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center gap-2">
                <span className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-sm">4</span>
                Or Run Locally
              </h4>
              <CodeBlock
                id="local"
                code={`# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py`}
              />
            </div>
          </div>
        </div>

        {/* File Structure */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 mb-12">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span>📁</span> Project Structure
          </h3>
          <pre className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto text-sm">
{`shopify-niche-intelligence/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
├── .env.example           # Environment variables template
│
├── config/                # Configuration
├── data_sources/          # Data fetching modules
├── analyzers/             # Analysis engines
├── scoring/               # Scoring systems
├── ui/                    # Streamlit UI components
├── utils/                 # Utility functions
└── tests/                 # Unit tests`}
          </pre>
        </div>

        {/* Requirements */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span>📋</span> Requirements
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-green-400 mb-3">✅ Compatible With</h4>
              <ul className="text-gray-400 space-y-2">
                <li>• Python 3.11 - 3.14</li>
                <li>• Streamlit Cloud</li>
                <li>• No system dependencies needed</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-blue-400 mb-3">📦 Key Dependencies</h4>
              <ul className="text-gray-400 space-y-2">
                <li>• streamlit {'>='} 1.32.0</li>
                <li>• pandas {'>='} 2.2.0</li>
                <li>• httpx {'>='} 0.27.0</li>
                <li>• beautifulsoup4 {'>='} 4.12.0</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-black/30 border-t border-white/10 mt-16">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center">
          <p className="text-gray-400">
            Built with Python + Streamlit • Only Verified Shopify Stores • No Fake Data
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Ready for Streamlit Cloud deployment
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
