# ChainSense

**streamlit now live at: https://chainsense-kd6ljtsanjhcw7ta7rjfyr.streamlit.app/**

Behavioral segmentation of Ethereum wallets. We're clustering ~6.3M wallets based on their on-chain activity alone (no token lists, no address labels). 

**Stack:** Python, DuckDB, Streamlit, XGBoost, HDBSCAN.

## Overview
The goal here is to take raw ethereum data (BigQuery public dataset), process it into features (volume, counterparty, timing, etc) and cluster them into archetypes using HDBSCAN. Then we serve it in real time via a Streamlit dashboard using XGBoost to classify new wallets on the fly. 

Main finding so far is isolating a big chunk of phishing-victim drain wallets purely from behavior, without any prior labels.

## Structure
- `pipeline/` - ETL (bronze to silver to gold), feature extraction, and ML models
- `app.py` - The Streamlit frontend dashboard
- `notebooks/` - Model training and exploration (mostly colab stuff)
- `docs/` - notes, slides, and diagrams
- `data/` - parquet files (gitignored obviously)

## Deployment

The entire stack (backend data + frontend dashboard) is unified in `app.py` and deployed on Streamlit Community Cloud.
