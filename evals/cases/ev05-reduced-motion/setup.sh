#!/bin/bash
set -euo pipefail
mkdir -p src
cat > src/HintPulse.tsx <<'TSX'
import Animated, { useSharedValue, useAnimatedStyle, withRepeat, withTiming } from 'react-native-reanimated';
import { useEffect } from 'react';

// The pulse is the only thing that tells the player which arrow the paid hint points at.
export function HintPulse({ active }: { active: boolean }) {
  const t = useSharedValue(0);
  useEffect(() => {
    t.value = active ? withRepeat(withTiming(1, { duration: 600 }), -1, true) : 0;
  }, [active]);
  const style = useAnimatedStyle(() => ({ opacity: 0.2 + 0.8 * t.value, transform: [{ scale: 1 + 0.15 * t.value }] }));
  return <Animated.View style={[{ width: 40, height: 40, borderRadius: 20, backgroundColor: '#E4327D' }, style]} />;
}
TSX
