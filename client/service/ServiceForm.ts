import type { AktrContext } from "../../core/AktrContext";
import { AktrElement, qs, qsa } from "../../core/AktrElement";
import type { AktrService, AktrServiceBuilder, AktrServiceArgs } from "../../core/AktrService";

export class ServiceForm {

    static builder: AktrServiceBuilder = (args: AktrServiceArgs) => {
        return (ctx: AktrContext) => {
            let form = qs(args.form);
            let inputs = qsa('input', form);
            let err = qs('.form-err', form);
            for (let i = 0; i < inputs.length; i++) {
                inputs[i].on('input', (e: Event) => {
                    args.validationFunc(inputs[i], err);
                });
            }
            
        }
    }

    static login: AktrService = ServiceForm.builder({
        form: '#login-form',
        validationFunc: (input: AktrElement, err: AktrElement) => {
            if (input.name() === 'email') {
                err.add('aktr-fade-out')
                setTimeout(() => {
                    err.add('invisible')
                }, 200)
            }
            if (input.name() === 'password') {
                err.add('aktr-fade-out')
                setTimeout(() => {
                    err.add('invisible')
                }, 200)
            }
        }
    })

}