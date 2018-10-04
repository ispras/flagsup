extern void foo();
extern void bar();
extern void baz();

int main() {
  volatile int i;

  switch (i) {
  case 0:
    foo();
    break;
  case 8:
    bar();
    break;
  case 15:
    baz();
    break;
  default:
    break;
  }
  return 0;
}
