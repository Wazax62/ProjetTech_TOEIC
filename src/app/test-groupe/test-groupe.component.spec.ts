import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TestGroupeComponent } from './test-groupe.component';



describe('ClassesComponent', () => {
  let component: TestGroupeComponent;
  let fixture: ComponentFixture<TestGroupeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestGroupeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TestGroupeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
