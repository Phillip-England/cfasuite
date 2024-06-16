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
      let ctx = {
        data: {},
        events: {}
      };
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

// client/core/AktrElement.ts
var qs = (selector, root = undefined) => {
  if (!root) {
    let el2 = document.querySelector(selector);
    if (!el2) {
      throw new Error(`AktrElement qs: element not found for selector ${selector}`);
    }
    return new AktrElement(document.querySelector(selector));
  }
  let rootElement = root.me;
  let el = rootElement.querySelector(selector);
  if (!el) {
    throw new Error(`AktrElement qs: element not found for selector ${selector}`);
  }
  return new AktrElement(el);
};
var qsa = (selector, root = undefined) => {
  if (!root) {
    return Array.from(document.querySelectorAll(selector)).map((e) => new AktrElement(e));
  }
  let rootElement = root.me;
  let els = rootElement.querySelectorAll(selector);
  if (!els) {
    throw new Error(`AktrElement qsa: elements not found for selector ${selector}`);
  }
  return Array.from(document.querySelectorAll(selector)).map((e) => new AktrElement(e));
};

class AktrElement {
  me;
  constructor(me) {
    this.me = me;
    this.me.setAttribute("aktr", "");
  }
  static addToAll(className, ...elements) {
    elements.forEach((e) => {
      e.add(className);
    });
  }
  static removeFromAll(className, ...elements) {
    elements.forEach((e) => {
      e.remove(className);
    });
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

// client/core/AktrContext.ts
class AktrContextWorker {
  static async storeEvent(ctx, key, event) {
    ctx.events[key] = event;
  }
  static async getEvent(ctx, key) {
    let events = ctx.events;
    if (!events) {
      throw new Error(`event with key ${key} not found in AktrContext`);
    }
    return events[key];
  }
  static async executeEvent(ctx, key) {
    let event = await AktrContextWorker.getEvent(ctx, key);
    await event();
  }
  static async storeData(ctx, key, data) {
    ctx.data[key] = data;
  }
  static async getData(ctx, key) {
    if (!ctx.data[key]) {
      throw new Error(`data with key ${key} not found in AktrContext`);
    }
    return ctx.data[key];
  }
}

// client/service/ServiceNav.ts
class ServiceNav {
  static builder = (args) => {
    return async (ctx) => {
      let bars = qs(args.bars);
      let nav = qs(args.nav);
      let overlay = qs(args.overlay);
      let loader = qs(args.loader);
      let navItems = qsa(".nav-item", nav);
      bars.on("click", async (e) => {
        AktrElement.removeFromAll("hidden", nav);
        AktrElement.addToAll("aktr-fade-in", nav);
        await AktrContextWorker.executeEvent(ctx, "overlay-fade-in");
        overlay.add("aktr-fade-in-half");
      });
      overlay.on("click", (e) => {
        AktrElement.removeFromAll("aktr-fade-in", nav);
        AktrElement.addToAll("aktr-fade-out", nav);
        overlay.remove("aktr-fade-in-half").add("aktr-fade-out-half");
        setTimeout(() => {
          AktrElement.addToAll("hidden", nav, overlay);
          AktrElement.removeFromAll("aktr-fade-out", nav);
          overlay.remove("aktr-fade-out-half");
        }, 200);
      });
      navItems.forEach((item) => {
        item.on("click", (e) => {
          AktrElement.addToAll("aktr-fade-out", nav);
          loader.remove("hidden").add("aktr-fade-in");
          setTimeout(() => {
            AktrElement.addToAll("hidden", nav);
            AktrElement.removeFromAll("aktr-fade-out", nav);
          }, 200);
        });
      });
    };
  };
  static admin = ServiceNav.builder({
    bars: "#header-bars",
    nav: "#nav",
    overlay: "#overlay",
    loader: "#main-loader"
  });
}

// client/service/ServiceForm.ts
class ServiceForm {
  static builder = (args) => {
    return async (ctx) => {
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

// client/service/ServiceOverlay.ts
class ServiceOverlay {
  static builder = (args) => {
    return async (ctx) => {
      let overlay = qs(args.overlay);
      AktrContextWorker.storeEvent(ctx, "overlay-fade-in", async () => {
        overlay.remove("hidden").add("aktr-fade-in");
      });
      AktrContextWorker.storeEvent(ctx, "overlay-fade-out", async () => {
        overlay.add("aktr-fade-out");
        setTimeout(() => {
          overlay.add("hidden").remove("aktr-fade-out");
        }, 200);
      });
    };
  };
  static overlay = ServiceOverlay.builder({
    overlay: "#overlay"
  });
}

// client/index.ts
var aktrRouter = new AktrRouter;
aktrRouter.add("/", ServiceOverlay.overlay, ServiceForm.login);
aktrRouter.add("/admin", ServiceOverlay.overlay, ServiceNav.admin);
