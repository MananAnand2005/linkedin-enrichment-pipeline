import { useState } from "react";

export default function App() {

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  // -----------------------------------
  // Upload Excel
  // -----------------------------------

  const handleFileUpload = async (event) => {

    const file = event.target.files[0];

    if (!file) return;

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
      "http://localhost:8000/upload-excel",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    setRows(data.rows);
  };

  // -----------------------------------
  // Run Enrichment
  // -----------------------------------

  const runEnrichment = async () => {

    setLoading(true);

    const response = await fetch(
      "http://localhost:8000/run-enrichment",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          rows: rows,
        }),
      }
    );

    const data = await response.json();

    setRows(data.rows);

    setLoading(false);
  };

  // -----------------------------------
  // Export Excel
  // -----------------------------------

  const exportResults = async () => {

    const response = await fetch(
      "http://localhost:8000/export-excel",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          rows: rows,
        }),
      }
    );

    const blob = await response.blob();

    const url = window.URL.createObjectURL(
      blob
    );

    const a = document.createElement("a");

    a.href = url;

    a.download = "enriched_results.xlsx";

    document.body.appendChild(a);

    a.click();

    a.remove();
  };

  return (

    <div className="min-h-screen bg-[#020B2D] text-white">

      <div className="max-w-7xl mx-auto px-10 py-10">

        {/* Header */}

        <div className="flex items-center justify-between mb-10">

          <div>

            <h1 className="text-4xl font-semibold tracking-wide">
              Enrichment Workspace
            </h1>

            <p className="text-white/60 mt-2 text-lg">
              AI-powered people intelligence pipeline
            </p>

          </div>

          <div className="text-right">

            <div className="text-2xl font-semibold">
              ION Analytics
            </div>

            <div className="text-sm text-white/50">
              Intelligence Platform
            </div>

          </div>

        </div>

        {/* Upload Card */}

        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 mb-8">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-2xl font-medium mb-2">
                Upload Lead File
              </h2>

              <p className="text-white/50">
                Upload Excel file containing leads
              </p>

            </div>

            <div className="flex gap-4">

              <input
                type="file"
                accept=".xlsx"
                onChange={handleFileUpload}
                className="
                  block
                  text-sm
                  text-white/80
                  file:mr-4
                  file:py-3
                  file:px-6
                  file:rounded-2xl
                  file:border-0
                  file:bg-[#18A0D8]
                  file:text-white
                  hover:file:opacity-90
                  cursor-pointer
                "
              />

              <button
                onClick={runEnrichment}
                disabled={loading || rows.length === 0}
                className="
                  px-6
                  py-3
                  rounded-2xl
                  bg-[#9AC86B]
                  text-black
                  font-medium
                  hover:opacity-90
                  disabled:opacity-40
                "
              >

                {loading
                  ? "Running..."
                  : "Run Enrichment"}

              </button>

              <button
                onClick={exportResults}
                disabled={rows.length === 0}
                className="
                  px-6
                  py-3
                  rounded-2xl
                  bg-white/10
                  border
                  border-white/10
                  text-white
                  hover:bg-white/20
                  disabled:opacity-40
                "
              >

                Export Results

              </button>

            </div>

          </div>

        </div>

        {/* Results Table */}

        <div className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden">

          {rows.length === 0 ? (

            <div className="px-6 py-16 text-center text-white/40">
              No leads uploaded yet
            </div>

          ) : (

            <>

              {/* Header */}

              <div
                className="
                  grid
                  bg-white/10
                  px-6
                  py-5
                  text-sm
                  uppercase
                  tracking-wider
                  text-white/60
                "
                style={{
                  gridTemplateColumns: `repeat(${Object.keys(rows[0]).length}, minmax(0, 1fr))`
                }}
              >

                {Object.keys(rows[0]).map((column) => (

                  <div
                    key={column}
                    className="font-medium truncate"
                  >
                    {column}
                  </div>

                ))}

              </div>

              {/* Rows */}

              {rows.map((row, index) => (

                <div
                  key={index}
                  className="
                    grid
                    px-6
                    py-5
                    border-t
                    border-white/5
                    hover:bg-white/[0.04]
                    transition
                  "
                  style={{
                    gridTemplateColumns: `repeat(${Object.keys(row).length}, minmax(0, 1fr))`
                  }}
                >

                  {Object.values(row).map((value, i) => (

                    <div
                      key={i}
                      className="text-white/80 truncate pr-4"
                    >

                      {String(value || "")}

                    </div>

                  ))}

                </div>

              ))}

            </>

          )}

        </div>

      </div>

    </div>
  );
}