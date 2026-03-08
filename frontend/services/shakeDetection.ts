/**
 * Shake Detection Service
 *
 * Detects shake gestures using device accelerometer
 * Uses expo-sensors to monitor device motion
 */

import { Accelerometer } from 'expo-sensors';

// Configuration
const SHAKE_THRESHOLD = 2.5; // Acceleration threshold (g-force)
const SHAKE_TIMEOUT_MS = 500; // Minimum time between shake events

class ShakeDetectionService {
  private subscription: any = null;
  private isEnabled: boolean = false;
  private lastShakeTime: number = 0;
  private listeners: Set<() => void> = new Set();

  /**
   * Start listening for shake gestures
   */
  async startDetection(): Promise<void> {
    try {
      // Set update interval (in milliseconds)
      Accelerometer.setUpdateInterval(100);

      // Subscribe to accelerometer updates
      this.subscription = Accelerometer.addListener(({ x, y, z }) => {
        // Calculate total acceleration magnitude
        const acceleration = Math.sqrt(x * x + y * y + z * z);

        // Check if acceleration exceeds threshold
        if (acceleration > SHAKE_THRESHOLD) {
          const now = Date.now();

          // Debounce: Only trigger if enough time has passed since last shake
          if (now - this.lastShakeTime > SHAKE_TIMEOUT_MS) {
            this.lastShakeTime = now;
            this.notifyListeners();
          }
        }
      });

      this.isEnabled = true;
      console.log('[SHAKE] Shake detection started');

    } catch (error) {
      console.error('[SHAKE] Failed to start shake detection:', error);
      throw error;
    }
  }

  /**
   * Stop listening for shake gestures
   */
  stopDetection(): void {
    if (this.subscription) {
      this.subscription.remove();
      this.subscription = null;
    }
    this.isEnabled = false;
    console.log('[SHAKE] Shake detection stopped');
  }

  /**
   * Subscribe to shake events
   * @returns Unsubscribe function
   */
  onShake(listener: () => void): () => void {
    this.listeners.add(listener);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Notify all listeners of shake event
   */
  private notifyListeners(): void {
    console.log('[SHAKE] Shake detected!');
    this.listeners.forEach(listener => listener());
  }

  /**
   * Check if shake detection is currently enabled
   */
  get enabled(): boolean {
    return this.isEnabled;
  }
}

// Export singleton instance
export const shakeDetection = new ShakeDetectionService();
