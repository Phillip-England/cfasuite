import type { AktrEvent, AktrEvents } from "./AktrEvent";



export type AktrContext = {
    data: {[key: string]: any};
    events: AktrEvents;
};

export class AktrContextWorker { 

    static async storeEvent(ctx: AktrContext, key: string, event: AktrEvent): Promise<void> {
        ctx.events[key] = event;
    }

    static async getEvent(ctx: AktrContext, key: string): Promise<AktrEvent> {
        let events = ctx.events;
        if (!events) {
            throw new Error(`event with key ${key} not found in AktrContext`);
        }
        return events[key];
    }

    static async executeEvent(ctx: AktrContext, key: string): Promise<void> {
        let event = await AktrContextWorker.getEvent(ctx, key);
        await event();
    }

    static async storeData(ctx: AktrContext, key: string, data: any): Promise<void> {
        ctx.data[key] = data;
    }

    static async getData(ctx: AktrContext, key: string): Promise<any> {
        if (!ctx.data[key]) {
            throw new Error(`data with key ${key} not found in AktrContext`);
        }
        return ctx.data[key];
    }



}

