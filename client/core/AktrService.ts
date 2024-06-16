import type { AktrContext } from './AktrContext';

export type AktrService = (ctx: AktrContext) => void;

export type AktrServiceArgs = { [key: string]: any };
export type AktrServiceBuilder = (args: AktrServiceArgs) => AktrService;