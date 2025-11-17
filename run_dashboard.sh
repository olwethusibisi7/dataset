#!/bin/bash

# Ensure script fails on any error
set -e

# Directory containing this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment if it exists
if command -v conda &> /dev/null; then
    if conda env list | grep -q "isazi-recruitment"; then
        echo "Activating conda environment: isazi-recruitment"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate isazi-recruitment
    else
        echo "Warning: conda environment 'isazi-recruitment' not found"
        echo "Create it with: conda create -n isazi-recruitment python=3.9"
        exit 1
    fi
fi

# Add the project root to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Check if required packages are installed
python -c "import streamlit, pandas, numpy, plotly" || {
    echo "Error: Missing required packages. Install them with:"
    echo "pip install streamlit pandas numpy plotly"
    exit 1
}

# Create sample data if database doesn't exist
python - <<EOF
try:
    from recruitment_functions import create_sample_data, load_recruitment_data
    create_sample_data()
    print("Database ready with sample data")
except Exception as e:
    print(f"Warning: Could not create sample data: {e}")
EOF

# Start Streamlit
echo "Starting dashboard at http://localhost:8501"
cd "${SCRIPT_DIR}"
streamlit run dashboard.py "$@"