
export type AktrEvent = () => Promise<void>
export type AktrEvents = {[key: string]: AktrEvent}