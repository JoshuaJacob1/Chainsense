# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.

from AlgorithmImports import *
from collections import deque
import numpy as np

class ArchetypeFlowAlphaModel(QCAlgorithm):
    """
    Hypothesis Test: Do smart-money archetype flows predict ETH price?
    Strategy: 168h rolling z-score of net flow. Entry on z > 1.0 (short). Liquidate after 72h.
    """
    
    def Initialize(self):
        # Window: 2025-05-05 00:00 -> 2026-05-04 23:59
        self.SetStartDate(2025, 5, 5)
        self.SetEndDate(2026, 5, 4)
        self.SetCash(100000)
        
        # Universe: Single asset ETH/USD hourly bars
        self.eth = self.AddCrypto("ETHUSD", Resolution.Hour).Symbol
        
        # 168h (1-week) rolling window for Z-score
        self.flow_window = deque(maxlen=168)
        self.entry_time = None
        
    def OnData(self, data):
        if not data.ContainsKey(self.eth):
            return
            
        # In a live QC environment, this pulls our archetype flow via custom data feed.
        # This simulates pulling the 'dex_aggregator_user' net flow.
        net_flow = self.GetArchetypeFlow("dex_aggregator_user")
        self.flow_window.append(net_flow)
        
        # Need a full week of data to compute a valid z-score
        if len(self.flow_window) < 168:
            return
            
        # Compute Rolling Z-Score
        flow_array = np.array(self.flow_window)
        mean = np.mean(flow_array)
        std = np.std(flow_array)
        
        if std == 0: 
            return
            
        z_score = (net_flow - mean) / std
        
        # Exit: Liquidate exactly 72h after entry, regardless of price
        if self.Portfolio.Invested:
            if self.Time >= self.entry_time + timedelta(hours=72):
                self.Liquidate()
                self.entry_time = None
            return
        
        # Entry: Short 95% of the portfolio if z > 1.0 at an hourly close, if flat
        if not self.Portfolio.Invested and z_score > 1.0:
            self.SetHoldings(self.eth, -0.95)
            self.entry_time = self.Time

    def GetArchetypeFlow(self, archetype_name):
        """
        Mock integration function. In production, this would deserialize 
        JSON from the ChainSense backend's historical / live API.
        """
        import random
        return random.gauss(0, 1)
