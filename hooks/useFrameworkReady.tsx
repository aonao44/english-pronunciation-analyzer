import { useEffect } from 'react';

export function useFrameworkReady() {
  useEffect(() => {
    // Expoフレームワークの初期化処理
    console.log('Expo framework ready');
  }, []);
}