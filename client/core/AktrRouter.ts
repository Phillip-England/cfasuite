import type { AktrService } from "./AktrService";
import type { AktrContext } from "./AktrContext";

export type AktrRoute = { [key: string]: AktrService[] }

export class AktrRouter {

    routes: AktrRoute;

    constructor() {
        this.routes = {};
    }
  
    add(path: string, ...services: AktrService[]) {
        this.routes[path] = services;
    }
  
    hydrate(path: string) {
        if (this.routes[path]) {
            let ctx: AktrContext = {
                data: {},
                events: {}
            }
            this.routes[path].forEach(async (service) => {
                try {
                    await service(ctx);
                } catch (e) {
                    console.error(`error at AktrRouter.hydrate()`);
                    console.error(e);
                }
            });
        } else {
            console.error(`route ${path} not found at AktrRouter.hydrate()`);
        }
    }

}