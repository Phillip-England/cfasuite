import type { AktrService, AktrServiceBuilder, AktrServiceArgs } from "../core/AktrService"
import { qs } from "../core/AktrElement"
import type { AktrContext } from "../core/AktrContext";


export class ServiceNav {

    static builder: AktrServiceBuilder = (args: AktrServiceArgs) => {
        return (ctx: AktrContext) => {
            let bars = qs(args.bars);
            let nav = qs(args.nav);
            let overlay = qs(args.overlay);
            bars.on('click', (e) => {
                nav.remove('hidden')
                nav.add('aktr-fade-in')
                overlay.remove('hidden')
                overlay.add('aktr-fade-in-half')
            });
            overlay.on('click', (e) => {
                nav.remove('aktr-fade-in').add('aktr-fade-out')
                overlay.remove('aktr-fade-in-half').add('aktr-fade-out-half')
                setTimeout(() => {
                    nav.add('hidden').remove('aktr-fade-out')
                    overlay.add('hidden').remove('aktr-fade-out-half')
                }, 200)
            });
        }
    }

    static admin: AktrService = ServiceNav.builder({
        bars: '#header-bars',
        nav: '#nav',
        overlay: '#nav-overlay'
    })


}