// client/core/AktrRouter.ts
class AktrRouter {
  routes;
  constructor() {
    this.routes = {};
  }
  add(path, ...services) {
    this.routes[path] = services;
  }
  hydrate(path) {
    if (this.routes[path]) {
      let ctx = {};
      this.routes[path].forEach((service) => {
        service(ctx);
      });
    } else {
      console.error(`route ${path} not found at AktrRouter.hydrate()`);
    }
  }
}

// client/core/AktrElement.ts
var qs = (selector, root = "document") => {
  if (root === "document") {
    let el2 = document.querySelector(selector);
    if (!el2) {
      console.error(`AktrElement qs: element not found for selector ${selector}`);
    }
    return new AktrElement(document.querySelector(selector));
  }
  let rootElement = root.me;
  let el = rootElement.querySelector(selector);
  if (!el) {
    console.error(`AktrElement qs: element not found for selector ${selector}`);
  }
  return new AktrElement(el);
};
var qsa = (selector, root = "document") => {
  if (root === "document") {
    return Array.from(document.querySelectorAll(selector)).map((e) => new AktrElement(e));
  }
  let rootElement = root.me;
  let els = rootElement.querySelectorAll(selector);
  if (!els) {
    console.error(`AktrElement qsa: elements not found for selector ${selector}`);
  }
  return Array.from(document.querySelectorAll(selector)).map((e) => new AktrElement(e));
};

class AktrElement {
  me;
  constructor(me) {
    this.me = me;
    this.me.setAttribute("aktr", "");
  }
  on(event, handler) {
    this.me.addEventListener(event, handler);
    return this;
  }
  add(...className) {
    className.forEach((c) => {
      this.me.classList.add(c);
    });
    return this;
  }
  remove(...className) {
    className.forEach((c) => {
      this.me.classList.remove(c);
    });
    return this;
  }
  has(className) {
    return this.me.classList.contains(className);
  }
  isHidden() {
    if (this.has("hidden") || this.has("invisible")) {
      return true;
    }
    return false;
  }
  isVisibile() {
    return !this.isHidden();
  }
  setAttr(name, value) {
    this.me.setAttribute(name, value);
    return this;
  }
  getAttr(name) {
    return this.me.getAttribute(name) || "";
  }
  value() {
    let elm = this.me;
    return elm.value;
  }
  name() {
    return this.me.getAttribute("name") || "";
  }
}

// client/service/ServiceNav.ts
class ServiceNav {
  static builder = (args) => {
    return (ctx) => {
      let bars = qs(args.bars);
      let nav = qs(args.nav);
      let overlay = qs(args.overlay);
      bars.on("click", (e) => {
        nav.remove("hidden");
        nav.add("aktr-fade-in");
        overlay.remove("hidden");
        overlay.add("aktr-fade-in-half");
      });
      overlay.on("click", (e) => {
        nav.remove("aktr-fade-in").add("aktr-fade-out");
        overlay.remove("aktr-fade-in-half").add("aktr-fade-out-half");
        setTimeout(() => {
          nav.add("hidden").remove("aktr-fade-out");
          overlay.add("hidden").remove("aktr-fade-out-half");
        }, 200);
      });
    };
  };
  static admin = ServiceNav.builder({
    bars: "#header-bars",
    nav: "#nav",
    overlay: "#nav-overlay"
  });
}

// client/service/ServiceForm.ts
class ServiceForm {
  static builder = (args) => {
    return (ctx) => {
      let form = qs(args.form);
      let inputs = qsa("input", form);
      let err = qs(".form-err", form);
      for (let i = 0;i < inputs.length; i++) {
        inputs[i].on("input", (e) => {
          args.validationFunc(inputs[i], err);
        });
      }
    };
  };
  static login = ServiceForm.builder({
    form: "#login-form",
    validationFunc: (input, err) => {
      if (input.name() === "email") {
        err.add("aktr-fade-out");
        setTimeout(() => {
          err.add("invisible");
        }, 200);
      }
      if (input.name() === "password") {
        err.add("aktr-fade-out");
        setTimeout(() => {
          err.add("invisible");
        }, 200);
      }
    }
  });
}

// client/index.ts
var aktrRouter = new AktrRouter;
aktrRouter.add("/", ServiceForm.login);
aktrRouter.add("/admin", ServiceNav.admin);
