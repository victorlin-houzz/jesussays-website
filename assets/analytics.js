import { analytics } from 'https://esm.sh/@heycatch/sdk@0.8.0';

analytics.init({
  projectKey: 'hck_pk_grr2XkGQSvUKKLbT3sDr4772vyaZcuIr',
  requestBatching: false,
  install: {
    framework: 'web',
    agent: 'codex',
  },
});
