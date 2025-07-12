class ReinforcementLearningExecution:
    def __init__(self, dataScraper, date, lookback=10, learning_rate=0.1):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for state features
        self.learning_rate = learning_rate  # Simulated learning rate
        
        # State variables to track market conditions and strategy performance
        self.prev_action = None  # Previous action (buy, sell, hold)
        self.prev_reward = 0  # Reward from previous action
        self.consecutive_losses = 0  # Track consecutive losing trades
        self.consecutive_wins = 0  # Track consecutive winning trades
        self.volatility_adaptation = 1.0  # Multiplier for thresholds based on volatility
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # In a real reinforcement learning model, we would:
        # 1. Observe the current state (market conditions)
        # 2. Choose an action based on learned policy (Q-values)
        # 3. Execute the action and observe reward
        # 4. Update the policy based on the reward
        
        # Since we can't actually implement RL here, we'll simulate adaptive behavior
        # by adjusting thresholds based on recent performance and market conditions
        
        # 1. Observe the current state
        state = self.get_state(curr_index)
        
        # 2. Calculate adaptive thresholds based on past performance
        buy_threshold = self.calculate_adaptive_threshold(state, "buy")
        
        # 3. Make decision based on current state and adaptive threshold
        buy_signal = self.calculate_buy_signal(curr_index, state)
        
        # 4. Update state based on decision
        if buy_signal > buy_threshold:
            self.update_state("buy", buy_signal)
            return True
        else:
            self.update_state("hold", 0)
            return False
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # Similar to buy, but for sell decisions
        state = self.get_state(curr_index)
        sell_threshold = self.calculate_adaptive_threshold(state, "sell")
        sell_signal = self.calculate_sell_signal(curr_index, state)
        
        if sell_signal > sell_threshold:
            self.update_state("sell", sell_signal)
            return True
        else:
            self.update_state("hold", 0)
            return False
    
    def get_state(self, end_index):
        """Calculate features that represent the current market state"""
        state = {}
        
        # 1. Recent price trend
        state["trend"] = self.calculate_trend(end_index)
        
        # 2. Volatility
        state["volatility"] = self.calculate_volatility(end_index)
        
        # 3. Volume profile
        state["volume_ratio"] = self.calculate_volume_ratio(end_index)
        
        # 4. Price momentum
        state["momentum"] = self.calculate_momentum(end_index, 5)
        
        # 5. Mean reversion signal
        state["mean_reversion"] = self.calculate_mean_reversion_signal(end_index)
        
        return state
    
    def calculate_adaptive_threshold(self, state, action_type):
        """Calculate adaptive threshold based on state and past performance"""
        # Base threshold
        base_threshold = 0.3
        
        # Adjust based on volatility
        volatility_adjustment = state["volatility"] * self.volatility_adaptation
        
        # Adjust based on past performance
        performance_adjustment = 0.0
        
        if self.consecutive_losses > 2:
            # More conservative after losses
            performance_adjustment += 0.1 * self.consecutive_losses
        
        if self.consecutive_wins > 2:
            # More aggressive after wins
            performance_adjustment -= 0.05 * self.consecutive_wins
        
        # Different adjustments for buy vs sell
        if action_type == "buy":
            # More conservative for buying in high volatility
            threshold = base_threshold + volatility_adjustment + performance_adjustment
        else:  # sell
            # More aggressive for selling in high volatility
            threshold = base_threshold + (volatility_adjustment / 2) + performance_adjustment
        
        # Ensure threshold is in reasonable range
        return max(0.1, min(threshold, 0.9))
    
    def calculate_buy_signal(self, end_index, state):
        """Calculate a buy signal strength based on current state"""
        # Combine multiple factors for buy signal
        
        # 1. Trend following component
        trend_signal = max(0, state["trend"])  # Only positive when trend is up
        
        # 2. Mean reversion component
        mean_rev_signal = max(0, state["mean_reversion"])  # Only positive when below mean
        
        # 3. Volume confirmation
        volume_signal = max(0, state["volume_ratio"] - 1.0)  # Positive when volume is above average
        
        # 4. Momentum confirmation
        momentum_signal = max(0, state["momentum"])  # Positive when momentum is up
        
        # Weighted combination
        if state["volatility"] > 0.5:
            # In high volatility, rely more on trend and volume
            signal = (0.4 * trend_signal + 0.1 * mean_rev_signal + 
                      0.3 * volume_signal + 0.2 * momentum_signal)
        else:
            # In low volatility, rely more on mean reversion
            signal = (0.2 * trend_signal + 0.4 * mean_rev_signal + 
                      0.2 * volume_signal + 0.2 * momentum_signal)
        
        return signal
    
    def calculate_sell_signal(self, end_index, state):
        """Calculate a sell signal strength based on current state"""
        # Combine multiple factors for sell signal
        
        # 1. Trend following component
        trend_signal = max(0, -state["trend"])  # Only positive when trend is down
        
        # 2. Mean reversion component (inverted from buy)
        mean_rev_signal = max(0, -state["mean_reversion"])  # Only positive when above mean
        
        # 3. Volume confirmation (same as buy, volume spike is relevant for both)
        volume_signal = max(0, state["volume_ratio"] - 1.0)
        
        # 4. Momentum confirmation (inverted from buy)
        momentum_signal = max(0, -state["momentum"])  # Positive when momentum is down
        
        # Weighted combination
        if state["volatility"] > 0.5:
            # In high volatility, be quicker to sell
            signal = (0.3 * trend_signal + 0.2 * mean_rev_signal + 
                      0.2 * volume_signal + 0.3 * momentum_signal)
        else:
            # In low volatility, more balanced
            signal = (0.25 * trend_signal + 0.25 * mean_rev_signal + 
                      0.25 * volume_signal + 0.25 * momentum_signal)
        
        return signal
    
    def update_state(self, action, signal_strength):
        """Update internal state based on action and outcome"""
        # Simulate reward based on signal strength
        # In a real RL system, reward would come from actual P&L
        reward = signal_strength - 0.3  # Positive when signal is strong, negative when weak
        
        # Update consecutive win/loss counters
        if reward > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif reward < 0:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Adapt volatility multiplier based on reward
        if self.prev_action == action and self.prev_reward * reward > 0:
            # If same action with same reward direction, reinforce
            self.volatility_adaptation *= (1 + self.learning_rate * abs(reward))
        elif self.prev_action == action and self.prev_reward * reward < 0:
            # If same action with opposite reward, reduce
            self.volatility_adaptation *= (1 - self.learning_rate * abs(reward))
        
        # Cap the adaptation factor
        self.volatility_adaptation = max(0.5, min(self.volatility_adaptation, 2.0))
        
        # Store current action and reward for next update
        self.prev_action = action
        self.prev_reward = reward
    
    def calculate_trend(self, end_index):
        """Calculate the normalized trend strength"""
        # Use linear regression slope
        prices = []
        for i in range(end_index - self.lookback + 1, end_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))
        
        n = len(prices)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(prices) / n
        
        numerator = sum((x[i] - mean_x) * (prices[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
            
        slope = numerator / denominator
        
        # Normalize by the average price
        normalized_slope = slope * n / mean_y
        
        # Return a value between -1 and 1
        return max(min(normalized_slope * 10, 1.0), -1.0)  # Scale for sensitivity
    
    def calculate_volatility(self, end_index):
        """Calculate normalized volatility"""
        returns = []
        for i in range(end_index - self.lookback + 1, end_index):
            price_t = float(self.dataScraper.getNumData(i, "Close"))
            price_t_1 = float(self.dataScraper.getNumData(i + 1, "Close"))
            returns.append((price_t - price_t_1) / price_t_1)
            
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in returns)
        std_dev = (sum_squared_diff / len(returns)) ** 0.5
        
        # Normalize to [0, 1] range (assuming max volatility of 5%)
        return min(std_dev / 0.05, 1.0)
    
    def calculate_volume_ratio(self, end_index):
        """Calculate current volume relative to average"""
        current_volume = float(self.dataScraper.getNumData(end_index, "Volume"))
        
        # Calculate average volume
        avg_volume = 0.0
        for i in range(end_index - self.lookback + 1, end_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= (self.lookback - 1)
        
        # Return ratio of current to average
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def calculate_momentum(self, end_index, window):
        """Calculate price momentum over the specified window"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        past_price = float(self.dataScraper.getNumData(end_index - window, "Close"))
        
        # Normalize to [-1, 1] range (assuming max momentum of 10%)
        momentum = (current_price - past_price) / past_price
        return max(min(momentum * 10, 1.0), -1.0)  # Scale for sensitivity
    
    def calculate_mean_reversion_signal(self, end_index):
        """Calculate mean reversion signal (deviation from moving average)"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        
        # Calculate moving average
        ma = 0.0
        for i in range(end_index - self.lookback + 1, end_index + 1):
            ma += float(self.dataScraper.getNumData(i, "Close"))
        ma /= self.lookback
        
        # Calculate normalized deviation from mean
        # Positive when price is below mean (buy signal for mean reversion)
        # Negative when price is above mean (sell signal for mean reversion)
        deviation = (ma - current_price) / ma
        
        # Scale to make more sensitive
        return max(min(deviation * 5, 1.0), -1.0)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"