import AsyncStorage from '@react-native-async-storage/async-storage';

const EXCHANGE_KEY = 'EXCHANGES_LIST';

export type ExchangeItem = {
  id: string;
  image: string;
  desc: string;
  latitude: number;
  longitude: number;
};

export async function saveExchange(item: ExchangeItem) {
  try {
    const existing = await AsyncStorage.getItem(EXCHANGE_KEY);
    const list = existing ? JSON.parse(existing) : [];
    list.push(item);
    await AsyncStorage.setItem(EXCHANGE_KEY, JSON.stringify(list));
  } catch (e) {
    console.error('Failed to save exchange:', e);
  }
}

export async function getExchanges(): Promise<ExchangeItem[]> {
  try {
    const existing = await AsyncStorage.getItem(EXCHANGE_KEY);
    return existing ? JSON.parse(existing) : [];
  } catch (e) {
    console.error('Failed to load exchanges:', e);
    return [];
  }
}
