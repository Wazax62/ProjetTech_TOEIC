import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdategroupComponent } from './updategroup.component';

describe('UpdategroupComponent', () => {
  let component: UpdategroupComponent;
  let fixture: ComponentFixture<UpdategroupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdategroupComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdategroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
