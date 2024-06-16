import { AktrRouter } from './core/AktrRouter';
import { ServiceNav } from './service/ServiceNav';
import { ServiceForm } from './service/ServiceForm';

const aktrRouter = new AktrRouter();

aktrRouter.add('/', ServiceForm.login);
aktrRouter.add('/admin', ServiceNav.admin);
  
  