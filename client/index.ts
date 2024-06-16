import { AktrRouter } from './core/AktrRouter';
import { ServiceNav } from './src/service/ServiceNav';
import { ServiceForm } from './src/service/ServiceForm';

const aktrRouter = new AktrRouter();

aktrRouter.add('/', ServiceForm.login);
aktrRouter.add('/admin', ServiceNav.admin);
  
  