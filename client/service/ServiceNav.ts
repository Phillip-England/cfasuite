import type { AktrService, AktrServiceBuilder, AktrServiceArgs } from "../core/AktrService"
import { AktrElement, qs, qsa } from "../core/AktrElement"
import type { AktrContext } from "../core/AktrContext";


export class ServiceNav {

    static builder: AktrServiceBuilder = (args: AktrServiceArgs) => {
        return (ctx: AktrContext) => {

            let bars = qs(args.bars);
            let nav = qs(args.nav);
            let overlay = qs(args.overlay);
            let loader = qs(args.loader);
            let navItems = qsa('.nav-item', nav);

            bars.on('click', (e) => {
                AktrElement.removeFromAll('hidden', nav, overlay)
                AktrElement.addToAll('aktr-fade-in', nav)
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
        overlay: '#nav-overlay',
        loader: '#nav-loader'
    })


}