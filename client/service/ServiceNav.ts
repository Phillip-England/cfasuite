import type { AktrService, AktrServiceBuilder, AktrServiceArgs } from "../core/AktrService"
import { AktrElement, qs, qsa } from "../core/AktrElement"
import { AktrContextWorker, type AktrContext } from "../core/AktrContext";


export class ServiceNav {

    static builder: AktrServiceBuilder = (args: AktrServiceArgs): AktrService => {
        return async (ctx: AktrContext) => {

            let bars = qs(args.bars);
            let nav = qs(args.nav);
            let overlay = qs(args.overlay);
            let loader = qs(args.loader);
            let navItems = qsa('.nav-item', nav);

            bars.on('click', async (e) => {
                AktrElement.removeFromAll('hidden', nav)
                AktrElement.addToAll('aktr-fade-in', nav)
                await AktrContextWorker.executeEvent(ctx, 'overlay-fade-in')
                overlay.add('aktr-fade-in-half')
            });

            overlay.on('click', (e) => {
                AktrElement.removeFromAll('aktr-fade-in', nav)
                AktrElement.addToAll('aktr-fade-out', nav)
                overlay.remove('aktr-fade-in-half').add('aktr-fade-out-half')
                setTimeout(() => {
                    AktrElement.addToAll('hidden', nav, overlay)
                    AktrElement.removeFromAll('aktr-fade-out', nav)
                    overlay.remove('aktr-fade-out-half')
                }, 200)
            });

            navItems.forEach(item => {
                item.on('click', (e) => {
                    AktrElement.addToAll('aktr-fade-out', nav)
                    loader.remove('hidden').add('aktr-fade-in')
                    setTimeout(() => {
                        AktrElement.addToAll('hidden', nav)
                        AktrElement.removeFromAll('aktr-fade-out', nav)
                    }, 200)
                })
            })

        }
    }

    static admin: AktrService = ServiceNav.builder({
        bars: '#header-bars',
        nav: '#nav',
        overlay: '#overlay',
        loader: '#main-loader'
    })


}