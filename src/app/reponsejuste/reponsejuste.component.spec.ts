import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReponseJusteComponent } from './reponsejuste.component';

describe('ReponsejusteComponent', () => {
  let component: ReponseJusteComponent;
  let fixture: ComponentFixture<ReponseJusteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReponseJusteComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReponseJusteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
