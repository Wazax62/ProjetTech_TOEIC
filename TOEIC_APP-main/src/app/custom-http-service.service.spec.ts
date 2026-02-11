import { TestBed } from '@angular/core/testing';

import { CustomHttpServiceService } from './custom-http-service.service';

describe('CustomHttpServiceService', () => {
  let service: CustomHttpServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CustomHttpServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
