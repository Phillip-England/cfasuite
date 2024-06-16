import { AktrContextWorker } from "../core/AktrContext";
import { qs } from "../core/AktrElement";
import type { AktrService, AktrServiceArgs, AktrServiceBuilder } from "../core/AktrService";



export class ServiceOverlay {

    static builder: AktrServiceBuilder = (args: AktrServiceArgs): AktrService => {
        return async (ctx) => {
            let overlay = qs(args.overlay);
            AktrContextWorker.storeEvent(ctx, 'overlay-fade-in', async () => {
                overlay.remove('hidden').add('aktr-fade-in');
            });
            AktrContextWorker.storeEvent(ctx, 'overlay-fade-out', async () => {
                overlay.add('aktr-fade-out');
                setTimeout(() => {
                    overlay.add('hidden').remove('aktr-fade-out');
                }, 200);
            });

        }
    }

    static overlay: AktrService = ServiceOverlay.builder({
        overlay: '#overlay',
    })

}