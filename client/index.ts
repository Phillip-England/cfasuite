import { AktrRouter } from './core/AktrRouter';
import { ServiceNav } from './service/ServiceNav';
import { ServiceForm } from './service/ServiceForm';
import { ServiceOverlay } from './service/ServiceOverlay';

const aktrRouter = new AktrRouter();

aktrRouter.add('/', ServiceOverlay.overlay, ServiceForm.login);
aktrRouter.add('/admin', ServiceOverlay.overlay, ServiceNav.admin);
  
  