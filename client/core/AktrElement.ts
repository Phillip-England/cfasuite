

export const qs = (selector: string, root: string | AktrElement = 'document'): AktrElement => {
    if (root === 'document') {
        let el = document.querySelector(selector) as HTMLElement;
        if (!el) {
            console.error(`AktrElement qs: element not found for selector ${selector}`);
        }
        return new AktrElement(document.querySelector(selector) as HTMLElement);
    }
    let rootElement = (root as AktrElement).me;
    let el = rootElement.querySelector(selector) as HTMLElement;
    if (!el) {
        console.error(`AktrElement qs: element not found for selector ${selector}`);
    }
    return new AktrElement(el);
}

export const qsa = (selector: string, root: string | AktrElement = "document"): AktrElement[] => {
    if (root === 'document') {
        return Array.from(document.querySelectorAll(selector)).map(e => new AktrElement(e as HTMLElement));
    }
    let rootElement = (root as AktrElement).me;
    let els = rootElement.querySelectorAll(selector);
    if (!els) {
        console.error(`AktrElement qsa: elements not found for selector ${selector}`);
    }
    return Array.from(document.querySelectorAll(selector)).map(e => new AktrElement(e as HTMLElement));
}

export class AktrElement {
    me: HTMLElement;

    constructor(me: HTMLElement) {
        this.me = me;
        this.me.setAttribute('aktr', '');
    }

    static addToAll(className: string, ...elements: AktrElement[]) {
        elements.forEach(e => {
            e.add(className);
        });
    }

    static removeFromAll(className: string, ...elements: AktrElement[]) {
        elements.forEach(e => {
            e.remove(className);
        });
    }

    on(event: string, handler: (e: Event) => void): AktrElement {
        this.me.addEventListener(event, handler);
        return this;
    }

    add(...className: string[]): AktrElement {
        className.forEach(c => {
            this.me.classList.add(c);
        });
        return this;
    }

    remove(...className: string[]): AktrElement {
        className.forEach(c => {
            this.me.classList.remove(c);
        });
        return this;
    }

    has(className: string): boolean {
        return this.me.classList.contains(className);
    }

    isHidden(): boolean {
        if (this.has('hidden') || this.has('invisible')) {
            return true;
        }
        return false;
    }

    isVisibile(): boolean {
        return !this.isHidden();
    }

    setAttr(name: string, value: string): AktrElement {
        this.me.setAttribute(name, value);
        return this;
    }

    getAttr(name: string): string {
        return this.me.getAttribute(name) || '';
    }

    value(): string {
        let elm = this.me as HTMLInputElement;
        return elm.value;
    }

    name(): string {
        return this.me.getAttribute('name') || '';
    }



}

