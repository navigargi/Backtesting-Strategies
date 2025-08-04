import numpy as np
import math
from scipy.signal import savgol_filter, argrelextrema
from scipy.fft import fft, fftfreq


class QuantumEntropyStrategy:
    def __init__(self, dataScraper, date,
                 resonance_window=11,
                 entanglement_window=7,
                 coherence_window=5,
                 max_position=10):
        self.date = date
        self.dataScraper = dataScraper
        self.resonance_window = resonance_window  # Quantum resonance detection
        self.entanglement_window = entanglement_window  # Price-volume entanglement
        self.coherence_window = coherence_window  # Market coherence measurement
        self.max_position = max_position  # Max position size

        # Quantum state variables
        self.position = 0
        self.phase_state = 0  # -1 = destructive, 0 = neutral, 1 = constructive
        self.last_trade_index = -100
        self.quantum_memory = []

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Minimum data requirement and cooldown
        if curr_index < max(self.resonance_window, self.entanglement_window, self.coherence_window) + 10:
            return False
        if curr_index <= self.last_trade_index + 2:  # Trade cooldown
            return False

        # Calculate quantum market features
        resonance = self.detect_quantum_resonance(curr_index)
        entanglement = self.compute_price_volume_entanglement(curr_index)
        coherence = self.measure_market_coherence(curr_index)

        # Update quantum memory
        self.update_quantum_memory(resonance, entanglement, coherence)

        # Constructive interference detection
        phase_shift = self.detect_phase_shift()

        # Buy conditions (quantum coherence breakout)
        buy_signal = (
                phase_shift == 1 and  # Constructive interference
                resonance > 0.85 and  # Strong resonance
                entanglement > 0.7 and  # High price-volume entanglement
                coherence > 0.75 and  # High market coherence
                self.position < self.max_position
        )

        if buy_signal:
            position_size = self.calculate_position_size(resonance, entanglement, coherence, curr_index)
            self.position = min(self.max_position, self.position + position_size)
            self.last_trade_index = curr_index
            self.phase_state = 1  # Set phase to constructive
            return True
        return False

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        if curr_index <= self.last_trade_index + 1:  # Prevent immediate reversal
            return False

        # Calculate exit conditions
        current_resonance = self.detect_quantum_resonance(curr_index)
        current_coherence = self.measure_market_coherence(curr_index)
        profit_ratio = self.calculate_profit_ratio(curr_index)

        # Exit conditions
        resonance_decay = current_resonance < 0.65
        coherence_loss = current_coherence < 0.6
        profit_target = profit_ratio > 0.0012  # 0.12% profit target
        stop_loss = self.check_stop_loss(curr_index)

        if self.position > 0 and (resonance_decay or coherence_loss or profit_target or stop_loss):
            self.position = 0
            self.last_trade_index = curr_index
            self.phase_state = 0  # Reset phase state
            return True
        return False

    # ------------------- Quantum Market Features ------------------- #
    def detect_quantum_resonance(self, curr_index):
        """Detect resonance frequencies in price movements"""
        prices = []
        for i in range(curr_index - self.resonance_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        # Compute logarithmic returns
        returns = np.diff(np.log(prices))
        if len(returns) < 5:
            return 0.5

        # Apply Savitzky-Golay filter for noise reduction
        smoothed = savgol_filter(returns, window_length=5, polyorder=2)

        # Compute FFT of returns
        fft_vals = fft(smoothed)
        freqs = fftfreq(len(smoothed))

        # Find dominant frequency
        dominant_idx = np.argmax(np.abs(fft_vals[1:len(fft_vals) // 2])) + 1
        dominant_freq = freqs[dominant_idx]

        # Resonance strength calculation
        power_spectrum = np.abs(fft_vals) ** 2
        total_power = np.sum(power_spectrum[1:len(power_spectrum) // 2])
        dominant_power = power_spectrum[dominant_idx]

        return dominant_power / total_power if total_power > 0 else 0

    def compute_price_volume_entanglement(self, curr_index):
        """Measure entanglement between price changes and volume"""
        prices = []
        volumes = []
        for i in range(curr_index - self.entanglement_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))
            volumes.append(float(self.dataScraper.getNumData(i, "Volume")))

        # Compute price changes and volume changes
        price_changes = np.diff(prices)
        volume_changes = np.diff(volumes)

        if len(price_changes) < 2:
            return 0.5

        # Normalize changes
        norm_price = (price_changes - np.mean(price_changes)) / (np.std(price_changes) + 1e-8)
        norm_volume = (volume_changes - np.mean(volume_changes)) / (np.std(volume_changes) + 1e-8)

        # Calculate quantum entanglement (mutual information)
        joint_dist = np.histogram2d(norm_price, norm_volume, bins=5)[0]
        joint_dist /= np.sum(joint_dist)

        # Marginal distributions
        p_price = np.sum(joint_dist, axis=1)
        p_volume = np.sum(joint_dist, axis=0)

        # Mutual information calculation
        mutual_info = 0
        for i in range(len(p_price)):
            for j in range(len(p_volume)):
                if joint_dist[i, j] > 0 and p_price[i] > 0 and p_volume[j] > 0:
                    mutual_info += joint_dist[i, j] * np.log(joint_dist[i, j] / (p_price[i] * p_volume[j]))

        # Normalize to 0-1 range
        return np.tanh(mutual_info)  # Using tanh for normalization

    def measure_market_coherence(self, curr_index):
        """Measure market coherence through phase alignment"""
        prices = []
        for i in range(curr_index - self.coherence_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        # Compute Hilbert transform for instantaneous phase
        analytic_signal = self.hilbert_transform(prices)
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))

        # Phase coherence calculation
        phase_diff = np.diff(instantaneous_phase)
        phase_coherence = np.abs(np.mean(np.exp(1j * phase_diff)))

        return phase_coherence

    def hilbert_transform(self, data):
        """Simple Hilbert transform implementation without scipy"""
        n = len(data)
        # Compute FFT
        fft_data = fft(data)

        # Create Hilbert transform filter
        h = np.zeros(n)
        if n % 2 == 0:
            h[0] = 1
            h[1:n // 2] = 2
            h[n // 2] = 1
        else:
            h[0] = 1
            h[1:(n + 1) // 2] = 2

        # Apply filter
        analytic_signal = np.fft.ifft(fft_data * h)
        return analytic_signal

    # ------------------- Quantum State Management ------------------- #
    def update_quantum_memory(self, resonance, entanglement, coherence):
        """Update quantum memory with current state"""
        self.quantum_memory.append((resonance, entanglement, coherence))
        # Keep only the last 5 states
        if len(self.quantum_memory) > 5:
            self.quantum_memory.pop(0)

    def detect_phase_shift(self):
        """Detect phase shift using quantum memory"""
        if len(self.quantum_memory) < 3:
            return 0

        # Compute state gradients
        res_grad = np.gradient([x[0] for x in self.quantum_memory])
        ent_grad = np.gradient([x[1] for x in self.quantum_memory])
        coh_grad = np.gradient([x[2] for x in self.quantum_memory])

        # Detect constructive interference (all gradients positive)
        if res_grad[-1] > 0 and ent_grad[-1] > 0 and coh_grad[-1] > 0:
            return 1  # Constructive phase
        # Detect destructive interference (all gradients negative)
        elif res_grad[-1] < 0 and ent_grad[-1] < 0 and coh_grad[-1] < 0:
            return -1  # Destructive phase
        return 0  # No phase shift

    # ------------------- Position Management ------------------- #
    def calculate_position_size(self, resonance, entanglement, coherence, curr_index):
        """Quantum position sizing based on signal strength"""
        # Signal strength calculation
        signal_strength = (resonance + entanglement + coherence) / 3

        # Volatility adjustment
        volatility = self.compute_volatility(curr_index)
        vol_adjust = 1.0 / (1 + 50 * volatility)

        return max(1, round(signal_strength * vol_adjust * self.max_position))

    def compute_volatility(self, curr_index, window=5):
        """Compute minute-level volatility"""
        prices = []
        for i in range(curr_index - window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        if len(prices) < 2:
            return 0

        returns = np.abs(np.diff(np.log(prices)))
        return np.mean(returns)

    def calculate_profit_ratio(self, curr_index):
        """Calculate unrealized profit ratio"""
        if self.position == 0 or self.last_trade_index < 0:
            return 0

        entry_price = float(self.dataScraper.getNumData(self.last_trade_index, "Close"))
        current_price = float(self.dataScraper.getNumData(curr_index, "Close"))
        return (current_price - entry_price) / entry_price

    def check_stop_loss(self, curr_index):
        """Volatility-based stop loss check"""
        if self.position == 0 or self.last_trade_index < 0:
            return False

        entry_price = float(self.dataScraper.getNumData(self.last_trade_index, "Close"))
        current_price = float(self.dataScraper.getNumData(curr_index, "Close"))
        volatility = self.compute_volatility(curr_index, window=10)

        # Dynamic stop loss at 2.5x volatility
        stop_level = entry_price * (1 - 2.5 * volatility)
        return current_price <= stop_level

    # ------------------- Utility Methods ------------------- #
    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"