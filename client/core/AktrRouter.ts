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
            let ctx: AktrContext = {}
            this.routes[path].forEach((service) => {
                service(ctx);
            });
        } else {
            console.error(`route ${path} not found at AktrRouter.hydrate()`);
        }
    }

}